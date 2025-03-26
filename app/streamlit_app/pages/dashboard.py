import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import asyncio
from app.data_collection.exchange_client import ExchangeClient
from app.data_collection.market_data import MarketDataManager
from app.trading.exchange_client import ExchangeClient as TradingExchangeClient
from app.config.config_manager import ConfigManager

# Get logger
logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def calculate_indicators(df):
    """Calculate technical indicators."""
    try:
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Calculate Bollinger Bands
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        df['BB_upper'] = df['BB_middle'] + 2 * df['close'].rolling(window=20).std()
        df['BB_lower'] = df['BB_middle'] - 2 * df['close'].rolling(window=20).std()
        
        return df
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return df

@st.cache_data(ttl=60)  # Cache for 1 minute
async def get_market_data(symbol='BTC/USDT', timeframe='1h', limit=100):
    """Get market data for a symbol."""
    try:
        exchange_client = ExchangeClient()
        df = exchange_client.get_historical_data(symbol, timeframe, limit)
        df = calculate_indicators(df)
        return df.to_dict()  # Convert to dict for caching
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        return None
    finally:
        exchange_client.close()

@st.cache_data(ttl=30)  # Cache for 30 seconds
async def get_portfolio_data():
    """Get real portfolio data from the exchange."""
    try:
        # Initialize exchange client
        exchange_client = ExchangeClient(debug=False)
        await exchange_client.initialize()
        
        # Get balance
        balance = await exchange_client.get_balance()
        
        if not balance:
            logger.warning("No balance data received")
            return None
            
        # Process balance data
        portfolio = {
            'assets': [],
            'total_value_usd': 0.0,
            'pnl_24h_pct': 0.0,  # This would need to be calculated from trade history
            'pnl_7d_pct': 0.0,   # This would need to be calculated from trade history
            'pnl_30d_pct': 0.0   # This would need to be calculated from trade history
        }
        
        # Process each asset
        for currency, amount in balance['total'].items():
            if amount > 0:  # Only include non-zero balances
                # Get current price in USDT
                if currency != 'USDT':
                    ticker = await exchange_client.get_ticker(f"{currency}/USDT")
                    if ticker and 'last' in ticker:
                        value_usd = amount * ticker['last']
                        portfolio['assets'].append({
                            'symbol': currency,
                            'amount': amount,
                            'value_usd': value_usd
                        })
                        portfolio['total_value_usd'] += value_usd
                else:
                    portfolio['assets'].append({
                        'symbol': currency,
                        'amount': amount,
                        'value_usd': amount
                    })
                    portfolio['total_value_usd'] += amount
        
        await exchange_client.close()
        return portfolio
        
    except Exception as e:
        logger.error(f"Error getting portfolio data: {e}")
        return None

@st.cache_data(ttl=30)  # Cache for 30 seconds
async def get_active_trades():
    """Get real active trades from the exchange."""
    try:
        # Initialize exchange client
        exchange_client = ExchangeClient(debug=False)
        await exchange_client.initialize()
        
        # Get open orders
        open_orders = await exchange_client.get_open_orders()
        
        if not open_orders:
            logger.info("No active trades found")
            return []
            
        # Process open orders
        trades = []
        for order in open_orders:
            # Get current price for the symbol
            ticker = await exchange_client.get_ticker(order['symbol'])
            if ticker and 'last' in ticker:
                current_price = ticker['last']
                entry_price = order['price']
                
                # Calculate PnL percentage
                if order['side'] == 'buy':
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                else:
                    pnl_pct = ((entry_price - current_price) / entry_price) * 100
                
                trades.append({
                    'id': order['id'],
                    'symbol': order['symbol'],
                    'type': order['side'].upper(),
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'pnl_pct': pnl_pct,
                    'strategy': order.get('strategy', 'manual'),
                    'timestamp': datetime.fromtimestamp(order['timestamp'] / 1000)
                })
        
        await exchange_client.close()
        return trades
        
    except Exception as e:
        logger.error(f"Error getting active trades: {e}")
        return []

@st.cache_data(ttl=60)  # Cache for 60 seconds
async def get_multiple_market_data(symbols=['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT'], timeframe='1h', limit=100):
    """Get market data for multiple symbols."""
    try:
        # Initialize exchange client
        exchange_client = ExchangeClient(debug=False)
        await exchange_client.initialize()
        
        # Get data for each symbol
        data_dict = {}
        for symbol in symbols:
            ohlcv = await exchange_client.get_ohlcv(symbol, timeframe, limit)
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                data_dict[symbol] = df['close']
        
        await exchange_client.close()
        
        # Create a DataFrame with all closing prices
        if data_dict:
            return pd.DataFrame(data_dict)
        return None
        
    except Exception as e:
        logger.error(f"Error getting multiple market data: {e}")
        return None

def analyze_market_conditions(returns, window=24):
    """Analyze market conditions based on returns and volatility."""
    # Calculate volatility
    volatility = returns.rolling(window=window).std() * np.sqrt(252)
    
    # Calculate market trend
    trend = returns.rolling(window=window).mean() * 252
    
    # Calculate market regime
    regime = pd.DataFrame(index=returns.index)
    regime['volatility'] = volatility.mean(axis=1)
    regime['trend'] = trend.mean(axis=1)
    
    # Define market regimes
    regime['market_regime'] = 'Unknown'
    regime.loc[(regime['volatility'] > regime['volatility'].quantile(0.7)) & (regime['trend'] > 0), 'market_regime'] = 'High Volatility Bull'
    regime.loc[(regime['volatility'] > regime['volatility'].quantile(0.7)) & (regime['trend'] < 0), 'market_regime'] = 'High Volatility Bear'
    regime.loc[(regime['volatility'] < regime['volatility'].quantile(0.3)) & (regime['trend'] > 0), 'market_regime'] = 'Low Volatility Bull'
    regime.loc[(regime['volatility'] < regime['volatility'].quantile(0.3)) & (regime['trend'] < 0), 'market_regime'] = 'Low Volatility Bear'
    
    return regime

def optimize_portfolio(returns, risk_free_rate=0.02):
    """Calculate optimal portfolio weights using Modern Portfolio Theory."""
    # Calculate mean returns and covariance matrix
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    # Calculate efficient frontier
    num_portfolios = 1000
    results = np.zeros((3, num_portfolios))
    weights_list = []
    
    for i in range(num_portfolios):
        # Generate random weights
        weights = np.random.random(len(returns.columns))
        weights = weights / np.sum(weights)
        weights_list.append(weights)
        
        # Calculate portfolio metrics
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        portfolio_sharpe = (portfolio_return - risk_free_rate) / portfolio_std
        
        results[0, i] = portfolio_return
        results[1, i] = portfolio_std
        results[2, i] = portfolio_sharpe
    
    # Find optimal portfolio (maximum Sharpe ratio)
    optimal_idx = np.argmax(results[2])
    optimal_weights = weights_list[optimal_idx]
    
    return {
        'optimal_weights': dict(zip(returns.columns, optimal_weights)),
        'expected_return': results[0, optimal_idx],
        'expected_volatility': results[1, optimal_idx],
        'sharpe_ratio': results[2, optimal_idx]
    }

def analyze_correlation_signals(returns, correlation_matrix, window=24):
    """Analyze correlation-based trading signals."""
    signals = []
    
    # Calculate rolling correlations
    rolling_corr = returns.rolling(window=window).corr()
    
    # Get current correlations
    current_corr = correlation_matrix.iloc[-1]
    
    # Analyze each pair
    for symbol1 in returns.columns:
        for symbol2 in returns.columns:
            if symbol1 != symbol2:
                # Get current correlation
                current_corr_value = current_corr[symbol1][symbol2]
                
                # Get historical correlation
                hist_corr = rolling_corr[symbol1][symbol2].mean()
                
                # Calculate correlation deviation
                corr_deviation = current_corr_value - hist_corr
                
                # Generate signals based on correlation changes
                if abs(corr_deviation) > 0.2:  # Significant deviation threshold
                    if corr_deviation > 0:
                        signals.append({
                            'type': 'correlation_increase',
                            'symbol1': symbol1,
                            'symbol2': symbol2,
                            'current_corr': current_corr_value,
                            'hist_corr': hist_corr,
                            'deviation': corr_deviation
                        })
                    else:
                        signals.append({
                            'type': 'correlation_decrease',
                            'symbol1': symbol1,
                            'symbol2': symbol2,
                            'current_corr': current_corr_value,
                            'hist_corr': hist_corr,
                            'deviation': corr_deviation
                        })
    
    return signals

def calculate_correlation_risk_metrics(returns, correlation_matrix, portfolio_weights):
    """Calculate correlation-based risk metrics."""
    # Calculate portfolio variance using correlation matrix
    cov_matrix = returns.cov() * 252  # Annualized covariance
    portfolio_variance = np.dot(portfolio_weights.T, np.dot(cov_matrix, portfolio_weights))
    portfolio_volatility = np.sqrt(portfolio_variance)
    
    # Calculate correlation-based risk contribution
    risk_contribution = {}
    for i, symbol in enumerate(returns.columns):
        # Calculate marginal risk contribution
        marginal_risk = np.dot(cov_matrix[i], portfolio_weights) / portfolio_volatility
        risk_contribution[symbol] = portfolio_weights[i] * marginal_risk
    
    # Calculate correlation-based position limits
    position_limits = {}
    for symbol in returns.columns:
        # Calculate correlation with portfolio
        portfolio_returns = np.sum(returns * portfolio_weights, axis=1)
        symbol_corr = returns[symbol].corr(portfolio_returns)
        
        # Set position limits based on correlation
        if abs(symbol_corr) > 0.7:
            position_limits[symbol] = 0.2  # 20% max for highly correlated assets
        elif abs(symbol_corr) > 0.5:
            position_limits[symbol] = 0.3  # 30% max for moderately correlated assets
        else:
            position_limits[symbol] = 0.4  # 40% max for lowly correlated assets
    
    return {
        'portfolio_volatility': portfolio_volatility,
        'risk_contribution': risk_contribution,
        'position_limits': position_limits
    }

def calculate_correlation_position_sizing(returns, correlation_matrix, portfolio_value, risk_per_trade=0.02):
    """Calculate position sizes based on correlation risk."""
    position_sizes = {}
    
    # Calculate portfolio volatility
    portfolio_returns = returns.mean(axis=1)
    portfolio_volatility = portfolio_returns.std() * np.sqrt(252)
    
    for symbol in returns.columns:
        # Calculate correlation with portfolio
        symbol_corr = returns[symbol].corr(portfolio_returns)
        
        # Calculate asset volatility
        asset_volatility = returns[symbol].std() * np.sqrt(252)
        
        # Calculate correlation-adjusted volatility
        corr_adjusted_vol = asset_volatility * (1 - abs(symbol_corr))
        
        # Calculate position size based on risk
        risk_amount = portfolio_value * risk_per_trade
        position_size = risk_amount / corr_adjusted_vol
        
        # Apply correlation-based limits
        if abs(symbol_corr) > 0.7:
            position_size *= 0.8  # Reduce size for highly correlated assets
        elif abs(symbol_corr) > 0.5:
            position_size *= 0.9  # Slightly reduce for moderately correlated assets
        
        position_sizes[symbol] = position_size
    
    return position_sizes

def detect_correlation_regime(returns, correlation_matrix, window=24):
    """Detect market regime based on correlation patterns."""
    # Calculate rolling correlations
    rolling_corr = returns.rolling(window=window).corr()
    
    # Calculate correlation regime metrics
    regime_metrics = {
        'correlation_strength': correlation_matrix.abs().mean().mean(),
        'correlation_stability': rolling_corr.std().mean().mean(),
        'correlation_trend': (correlation_matrix - rolling_corr.mean()).mean().mean()
    }
    
    # Define correlation regimes
    if regime_metrics['correlation_strength'] > 0.7:
        regime = 'High Correlation'
    elif regime_metrics['correlation_strength'] > 0.5:
        regime = 'Moderate Correlation'
    else:
        regime = 'Low Correlation'
    
    # Add stability classification
    if regime_metrics['correlation_stability'] > 0.2:
        regime += ' (Unstable)'
    else:
        regime += ' (Stable)'
    
    return regime, regime_metrics

def find_arbitrage_opportunities(returns, correlation_matrix, price_data):
    """Find correlation-based arbitrage opportunities."""
    opportunities = []
    
    # Calculate rolling correlations
    rolling_corr = returns.rolling(window=24).corr()
    
    # Find highly correlated pairs
    for symbol1 in returns.columns:
        for symbol2 in returns.columns:
            if symbol1 != symbol2:
                # Get current correlation
                current_corr = correlation_matrix[symbol1][symbol2]
                
                # Get historical correlation
                hist_corr = rolling_corr[symbol1][symbol2].mean()
                
                # Calculate price ratio
                price_ratio = price_data[symbol1] / price_data[symbol2]
                current_ratio = price_ratio.iloc[-1]
                hist_ratio = price_ratio.mean()
                
                # Calculate deviation
                ratio_deviation = (current_ratio - hist_ratio) / hist_ratio
                
                # Check for arbitrage opportunity
                if abs(current_corr) > 0.8 and abs(ratio_deviation) > 0.02:
                    opportunities.append({
                        'pair': f"{symbol1}/{symbol2}",
                        'correlation': current_corr,
                        'deviation': ratio_deviation,
                        'current_ratio': current_ratio,
                        'historical_ratio': hist_ratio
                    })
    
    return opportunities

def calculate_risk_adjusted_metrics(returns, correlation_matrix, portfolio_weights):
    """Calculate correlation-based risk-adjusted performance metrics."""
    # Calculate portfolio returns
    portfolio_returns = np.sum(returns * portfolio_weights, axis=1)
    
    # Calculate metrics
    metrics = {}
    
    # Sharpe Ratio
    risk_free_rate = 0.02  # 2% annual risk-free rate
    excess_returns = portfolio_returns - risk_free_rate/252
    sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    metrics['sharpe_ratio'] = sharpe
    
    # Sortino Ratio
    downside_returns = excess_returns[excess_returns < 0]
    sortino = np.sqrt(252) * excess_returns.mean() / downside_returns.std()
    metrics['sortino_ratio'] = sortino
    
    # Information Ratio
    benchmark_returns = returns['BTC/USDT']  # Using BTC as benchmark
    tracking_error = (portfolio_returns - benchmark_returns).std()
    information_ratio = np.sqrt(252) * (portfolio_returns - benchmark_returns).mean() / tracking_error
    metrics['information_ratio'] = information_ratio
    
    # Correlation-adjusted returns
    correlation_penalty = 1 - abs(correlation_matrix.mean().mean())
    metrics['correlation_adjusted_return'] = excess_returns.mean() * correlation_penalty
    
    return metrics

def stress_test_portfolio(returns, correlation_matrix, portfolio_weights, scenarios=1000):
    """Perform correlation-based portfolio stress testing."""
    # Generate correlation scenarios
    stress_results = []
    
    for _ in range(scenarios):
        # Simulate correlation changes
        correlation_shock = np.random.normal(0, 0.2, correlation_matrix.shape)
        shocked_correlation = correlation_matrix + correlation_shock
        shocked_correlation = np.clip(shocked_correlation, -1, 1)
        
        # Calculate portfolio value change
        cov_matrix = returns.cov() * 252
        portfolio_variance = np.dot(portfolio_weights.T, np.dot(cov_matrix, portfolio_weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        # Simulate returns
        simulated_returns = np.random.normal(0, portfolio_volatility, 1)
        
        stress_results.append({
            'correlation_shock': correlation_shock.mean(),
            'portfolio_change': simulated_returns[0]
        })
    
    # Calculate stress test metrics
    stress_metrics = {
        'var_95': np.percentile([r['portfolio_change'] for r in stress_results], 5),
        'cvar_95': np.mean([r['portfolio_change'] for r in stress_results if r['portfolio_change'] <= np.percentile([r['portfolio_change'] for r in stress_results], 5)]),
        'max_loss': min([r['portfolio_change'] for r in stress_results]),
        'correlation_impact': np.mean([r['correlation_shock'] for r in stress_results])
    }
    
    return stress_metrics

def generate_hedging_suggestions(returns, correlation_matrix, portfolio_weights):
    """Generate correlation-based hedging suggestions."""
    suggestions = []
    
    # Calculate portfolio exposure
    portfolio_returns = np.sum(returns * portfolio_weights, axis=1)
    
    for symbol in returns.columns:
        if symbol != 'BTC/USDT':  # Skip BTC as it's our benchmark
            # Calculate correlation with portfolio
            symbol_corr = returns[symbol].corr(portfolio_returns)
            
            # Calculate hedge ratio
            hedge_ratio = -symbol_corr
            
            # Generate suggestion based on correlation
            if abs(symbol_corr) > 0.7:
                suggestions.append({
                    'symbol': symbol,
                    'correlation': symbol_corr,
                    'hedge_ratio': hedge_ratio,
                    'suggestion': f"Strong hedge candidate - Consider {abs(hedge_ratio):.2%} short position"
                })
            elif abs(symbol_corr) > 0.5:
                suggestions.append({
                    'symbol': symbol,
                    'correlation': symbol_corr,
                    'hedge_ratio': hedge_ratio,
                    'suggestion': f"Moderate hedge candidate - Consider {abs(hedge_ratio):.2%} short position"
                })
    
    return suggestions

def show(config):
    """Render the dashboard page."""
    st.title("Dashboard")
    
    # Get data for the dashboard
    try:
        # Get real market data
        market_data_dict = asyncio.run(get_market_data())
        if market_data_dict:
            market_data = pd.DataFrame.from_dict(market_data_dict)
        else:
            market_data = None
            
        portfolio = asyncio.run(get_portfolio_data())
        active_trades = asyncio.run(get_active_trades())
        
        if market_data is None or portfolio is None:
            st.error("Failed to load market data. Please check your exchange connection.")
            return
        
        # Auto-refresh functionality
        refresh_interval = config.get('ui', {}).get('refresh_rate', 5)
        st.empty()
        
        # Last updated timestamp
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_updated_container = st.container()
        
        with last_updated_container:
            cols = st.columns([3, 1])
            cols[1].markdown(f"**Last Updated:** {last_updated}")
            
            # Auto-refresh toggle
            auto_refresh = cols[0].checkbox("Auto-refresh data", value=True)
        
        # Display market overview
        st.subheader("Market Overview")
        
        # Add timeframe selector
        timeframe = st.selectbox(
            "Select Timeframe",
            ["1h", "4h", "1d"],
            index=0
        )
        
        # Add chart type selector
        chart_type = st.selectbox(
            "Select Chart Type",
            ["Line", "Candlestick", "Area"],
            index=0
        )
        
        # Add indicator selector
        indicators = st.multiselect(
            "Select Technical Indicators",
            ["RSI", "MACD", "Bollinger Bands", "Stochastic", "ATR", "Volume", "ROC", "ADX"],
            default=["RSI", "MACD"]
        )
        
        # Create subplots for price and indicators
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=('Price', 'Indicators', 'Volume'),
            row_heights=[0.5, 0.3, 0.2]
        )
        
        # Add price chart
        if chart_type == "Line":
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['close'],
                mode='lines',
                name='BTC/USDT',
                line=dict(color='#1E88E5', width=2)
            ), row=1, col=1)
        elif chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=market_data.index,
                open=market_data['open'],
                high=market_data['high'],
                low=market_data['low'],
                close=market_data['close'],
                name='BTC/USDT'
            ), row=1, col=1)
        else:  # Area
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['close'],
                mode='lines',
                name='BTC/USDT',
                line=dict(color='#1E88E5', width=2),
                fill='tozeroy'
            ), row=1, col=1)
        
        # Add selected indicators
        if "RSI" in indicators:
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='#FF9800', width=1)
            ), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        if "MACD" in indicators:
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='#1E88E5', width=1)
            ), row=2, col=1)
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['Signal'],
                mode='lines',
                name='Signal',
                line=dict(color='#FF9800', width=1)
            ), row=2, col=1)
            fig.add_trace(go.Bar(
                x=market_data.index,
                y=market_data['MACD_Hist'],
                name='MACD Hist',
                marker_color='#4CAF50'
            ), row=2, col=1)
        
        if "Bollinger Bands" in indicators:
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['BB_upper'],
                mode='lines',
                name='Upper BB',
                line=dict(color='#4CAF50', width=1, dash='dash')
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['BB_lower'],
                mode='lines',
                name='Lower BB',
                line=dict(color='#4CAF50', width=1, dash='dash')
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['BB_middle'],
                mode='lines',
                name='SMA',
                line=dict(color='#FF9800', width=1)
            ), row=1, col=1)
        
        if "Stochastic" in indicators:
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['%K'],
                mode='lines',
                name='%K',
                line=dict(color='#1E88E5', width=1)
            ), row=2, col=1)
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['%D'],
                mode='lines',
                name='%D',
                line=dict(color='#FF9800', width=1)
            ), row=2, col=1)
            fig.add_hline(y=80, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=20, line_dash="dash", line_color="green", row=2, col=1)
        
        if "ATR" in indicators:
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['ATR'],
                mode='lines',
                name='ATR',
                line=dict(color='#9C27B0', width=1)
            ), row=2, col=1)
        
        if "Volume" in indicators:
            fig.add_trace(go.Bar(
                x=market_data.index,
                y=market_data['volume'],
                name='Volume',
                marker_color='#1E88E5'
            ), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['Volume_SMA'],
                mode='lines',
                name='Volume SMA',
                line=dict(color='#FF9800', width=1)
            ), row=3, col=1)
        
        if "ROC" in indicators:
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['ROC'],
                mode='lines',
                name='ROC',
                line=dict(color='#E91E63', width=1)
            ), row=2, col=1)
        
        if "ADX" in indicators:
            fig.add_trace(go.Scatter(
                x=market_data.index,
                y=market_data['ADX'],
                mode='lines',
                name='ADX',
                line=dict(color='#795548', width=1)
            ), row=2, col=1)
            fig.add_hline(y=25, line_dash="dash", line_color="gray", row=2, col=1)
        
        # Update layout
        fig.update_layout(
            height=1000,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_title="Time",
            yaxis_title="Price (USDT)",
            yaxis2_title="Indicator Value",
            yaxis3_title="Volume",
            template="plotly_dark",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add technical analysis summary
        st.subheader("Technical Analysis Summary")
        
        # Calculate current indicator values
        current_price = market_data['close'].iloc[-1]
        current_rsi = market_data['RSI'].iloc[-1]
        current_macd = market_data['MACD'].iloc[-1]
        current_signal = market_data['Signal'].iloc[-1]
        current_bb_upper = market_data['BB_upper'].iloc[-1]
        current_bb_lower = market_data['BB_lower'].iloc[-1]
        current_stoch_k = market_data['%K'].iloc[-1]
        current_stoch_d = market_data['%D'].iloc[-1]
        current_adx = market_data['ADX'].iloc[-1]
        
        # Create analysis summary
        analysis = []
        
        # RSI Analysis
        if current_rsi > 70:
            analysis.append("RSI indicates overbought conditions")
        elif current_rsi < 30:
            analysis.append("RSI indicates oversold conditions")
        
        # MACD Analysis
        if current_macd > current_signal:
            analysis.append("MACD shows bullish momentum")
        else:
            analysis.append("MACD shows bearish momentum")
        
        # Bollinger Bands Analysis
        if current_price > current_bb_upper:
            analysis.append("Price is above upper Bollinger Band")
        elif current_price < current_bb_lower:
            analysis.append("Price is below lower Bollinger Band")
        
        # Stochastic Analysis
        if current_stoch_k > 80 and current_stoch_d > 80:
            analysis.append("Stochastic indicates overbought conditions")
        elif current_stoch_k < 20 and current_stoch_d < 20:
            analysis.append("Stochastic indicates oversold conditions")
        
        # ADX Analysis
        if current_adx > 25:
            analysis.append("Strong trend indicated by ADX")
        else:
            analysis.append("Weak trend indicated by ADX")
        
        # Display analysis
        for point in analysis:
            st.info(point)
        
        # Add correlation analysis section
        st.subheader("Asset Correlation Analysis")
        
        # Get data for multiple assets
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT']
        multi_data = asyncio.run(get_multiple_market_data(symbols, timeframe))
        
        if multi_data is not None:
            # Calculate returns
            returns = multi_data.pct_change()
            
            # Calculate correlation matrix
            correlation_matrix = returns.corr()
            
            # Create heatmap
            fig_corr = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.index,
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlation_matrix.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig_corr.update_layout(
                title='Asset Correlation Heatmap',
                height=500,
                margin=dict(l=0, r=0, t=30, b=0),
                template="plotly_dark"
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Add correlation-based trading signals
            st.subheader("Correlation-Based Trading Signals")
            
            # Analyze correlation signals
            signals = analyze_correlation_signals(returns, correlation_matrix)
            
            if signals:
                # Create a DataFrame for signals
                signals_df = pd.DataFrame(signals)
                
                # Format the signals for display
                signals_df['signal'] = signals_df.apply(
                    lambda x: f"{x['symbol1']} ↔ {x['symbol2']}: {'Increasing' if x['type'] == 'correlation_increase' else 'Decreasing'} correlation",
                    axis=1
                )
                signals_df['current_corr'] = signals_df['current_corr'].apply(lambda x: f"{x:.2f}")
                signals_df['hist_corr'] = signals_df['hist_corr'].apply(lambda x: f"{x:.2f}")
                signals_df['deviation'] = signals_df['deviation'].apply(lambda x: f"{x:+.2f}")
                
                # Display signals with color coding
                def color_signal(val):
                    try:
                        if 'Increasing' in val:
                            return 'color: green'
                        else:
                            return 'color: red'
                    except:
                        return ''
                
                styled_signals = signals_df.style.applymap(color_signal, subset=['signal'])
                st.dataframe(styled_signals[['signal', 'current_corr', 'hist_corr', 'deviation']], hide_index=True)
                
                # Add trading suggestions
                st.markdown("**Trading Suggestions:**")
                
                for signal in signals:
                    if signal['type'] == 'correlation_increase':
                        st.info(f"Consider pair trading: Long {signal['symbol1']} and Long {signal['symbol2']} "
                               f"(increasing correlation: {signal['current_corr']:.2f})")
                    else:
                        st.info(f"Consider pair trading: Long {signal['symbol1']} and Short {signal['symbol2']} "
                               f"(decreasing correlation: {signal['current_corr']:.2f})")
            else:
                st.info("No significant correlation changes detected at the moment.")
            
            # Add correlation insights
            st.subheader("Correlation Insights")
            
            # Find strongest correlations
            correlations = correlation_matrix.unstack()
            correlations = correlations[correlations != 1.0]  # Remove self-correlations
            strongest_pos = correlations.nlargest(3)
            strongest_neg = correlations.nsmallest(3)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Strongest Positive Correlations:**")
                for pair, corr in strongest_pos.items():
                    st.markdown(f"- {pair[0]} ↔ {pair[1]}: {corr:.2f}")
            
            with col2:
                st.markdown("**Strongest Negative Correlations:**")
                for pair, corr in strongest_neg.items():
                    st.markdown(f"- {pair[0]} ↔ {pair[1]}: {corr:.2f}")
            
            # Add correlation trend analysis
            st.markdown("**Correlation Trends:**")
            
            # Calculate rolling correlations
            rolling_corr = returns.rolling(window=24).corr()
            
            # Create trend plot
            fig_trend = go.Figure()
            
            for symbol in symbols:
                if symbol != 'BTC/USDT':  # Use BTC as reference
                    trend = rolling_corr.xs('BTC/USDT')[symbol]
                    fig_trend.add_trace(go.Scatter(
                        x=trend.index,
                        y=trend.values,
                        mode='lines',
                        name=f'{symbol} vs BTC',
                        line=dict(width=1)
                    ))
            
            fig_trend.update_layout(
                title='Rolling Correlation with BTC (24 periods)',
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                template="plotly_dark",
                yaxis_title="Correlation",
                xaxis_title="Time"
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Add market conditions analysis
        st.subheader("Market Conditions Analysis")
        
        if multi_data is not None:
            # Calculate returns
            returns = multi_data.pct_change()
            
            # Analyze market conditions
            regime = analyze_market_conditions(returns)
            current_regime = regime['market_regime'].iloc[-1]
            
            # Display current market regime
            regime_color = {
                'High Volatility Bull': 'green',
                'High Volatility Bear': 'red',
                'Low Volatility Bull': 'lightgreen',
                'Low Volatility Bear': 'pink',
                'Unknown': 'gray'
            }
            
            st.markdown(f"**Current Market Regime:** <span style='color: {regime_color[current_regime]}'>{current_regime}</span>", 
                       unsafe_allow_html=True)
            
            # Create regime transition plot
            fig_regime = go.Figure()
            
            for regime_type in regime['market_regime'].unique():
                mask = regime['market_regime'] == regime_type
                fig_regime.add_trace(go.Scatter(
                    x=regime[mask].index,
                    y=regime[mask]['trend'],
                    mode='markers',
                    name=regime_type,
                    marker=dict(size=8)
                ))
            
            fig_regime.update_layout(
                title='Market Regime Transitions',
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                template="plotly_dark",
                yaxis_title="Market Trend",
                xaxis_title="Time"
            )
            
            st.plotly_chart(fig_regime, use_container_width=True)
            
            # Add portfolio optimization
            st.subheader("Portfolio Optimization")
            
            # Calculate optimal portfolio
            optimal = optimize_portfolio(returns)
            
            # Display optimal weights
            st.markdown("**Optimal Portfolio Weights:**")
            weights_df = pd.DataFrame.from_dict(optimal['optimal_weights'], orient='index', columns=['Weight'])
            weights_df['Weight'] = weights_df['Weight'].apply(lambda x: f"{x:.2%}")
            st.dataframe(weights_df)
            
            # Display portfolio metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Expected Return", f"{optimal['expected_return']:.2%}")
            col2.metric("Expected Volatility", f"{optimal['expected_volatility']:.2%}")
            col3.metric("Sharpe Ratio", f"{optimal['sharpe_ratio']:.2f}")
            
            # Compare current vs optimal portfolio
            st.markdown("**Current vs Optimal Portfolio Comparison:**")
            
            # Get current portfolio weights
            current_weights = {}
            for asset in portfolio['assets']:
                symbol = asset['symbol']
                if symbol != 'USDT':
                    current_weights[f"{symbol}/USDT"] = asset['value_usd'] / portfolio['total_value_usd']
            
            # Create comparison DataFrame
            comparison_df = pd.DataFrame({
                'Current': pd.Series(current_weights),
                'Optimal': pd.Series(optimal['optimal_weights'])
            }).fillna(0)
            
            comparison_df['Difference'] = comparison_df['Optimal'] - comparison_df['Current']
            comparison_df['Difference'] = comparison_df['Difference'].apply(lambda x: f"{x:+.2%}")
            
            st.dataframe(comparison_df)
            
            # Add rebalancing suggestions
            st.markdown("**Portfolio Rebalancing Suggestions:**")
            
            for symbol, diff in comparison_df['Difference'].items():
                if float(diff.strip('%+')) > 5:  # Only show significant differences
                    action = "increase" if diff.startswith('+') else "decrease"
                    st.info(f"Consider to {action} position in {symbol} by {abs(float(diff.strip('%+'))):.1f}%")
        
        # Add correlation-based risk metrics
        st.subheader("Correlation-Based Risk Analysis")
        
        if multi_data is not None:
            # Calculate returns
            returns = multi_data.pct_change()
            
            # Calculate correlation matrix
            correlation_matrix = returns.corr()
            
            # Get current portfolio weights
            current_weights = {}
            for asset in portfolio['assets']:
                symbol = asset['symbol']
                if symbol != 'USDT':
                    current_weights[f"{symbol}/USDT"] = asset['value_usd'] / portfolio['total_value_usd']
            
            # Convert weights to numpy array
            weights_array = np.array([current_weights.get(symbol, 0) for symbol in returns.columns])
            
            # Calculate risk metrics
            risk_metrics = calculate_correlation_risk_metrics(returns, correlation_matrix, weights_array)
            
            # Display portfolio risk metrics
            col1, col2 = st.columns(2)
            col1.metric("Portfolio Volatility", f"{risk_metrics['portfolio_volatility']:.2%}")
            col2.metric("Risk per Trade", "2%")
            
            # Display risk contribution
            st.markdown("**Risk Contribution by Asset:**")
            risk_contribution_df = pd.DataFrame.from_dict(
                risk_metrics['risk_contribution'],
                orient='index',
                columns=['Risk Contribution']
            )
            risk_contribution_df['Risk Contribution'] = risk_contribution_df['Risk Contribution'].apply(lambda x: f"{x:.2%}")
            st.dataframe(risk_contribution_df)
            
            # Display position limits
            st.markdown("**Correlation-Based Position Limits:**")
            position_limits_df = pd.DataFrame.from_dict(
                risk_metrics['position_limits'],
                orient='index',
                columns=['Max Position Size']
            )
            position_limits_df['Max Position Size'] = position_limits_df['Max Position Size'].apply(lambda x: f"{x:.1%}")
            st.dataframe(position_limits_df)
            
            # Calculate and display position sizing
            st.markdown("**Correlation-Based Position Sizing:**")
            position_sizes = calculate_correlation_position_sizing(
                returns,
                correlation_matrix,
                portfolio['total_value_usd']
            )
            
            position_sizes_df = pd.DataFrame.from_dict(
                position_sizes,
                orient='index',
                columns=['Position Size (USDT)']
            )
            position_sizes_df['Position Size (USDT)'] = position_sizes_df['Position Size (USDT)'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(position_sizes_df)
            
            # Add risk warnings
            st.markdown("**Risk Warnings:**")
            for symbol, weight in current_weights.items():
                if weight > risk_metrics['position_limits'].get(symbol, 0.4):
                    st.warning(f"⚠️ {symbol} position ({weight:.1%}) exceeds correlation-based limit "
                             f"({risk_metrics['position_limits'].get(symbol, 0.4):.1%})")
            
            # Add correlation-based stop-loss levels
            st.markdown("**Correlation-Based Stop-Loss Levels:**")
            stop_loss_levels = {}
            for symbol in returns.columns:
                # Calculate volatility-based stop-loss
                volatility = returns[symbol].std() * np.sqrt(252)
                # Adjust stop-loss based on correlation
                symbol_corr = returns[symbol].corr(portfolio_returns)
                if abs(symbol_corr) > 0.7:
                    stop_loss = volatility * 1.5  # Tighter stop for highly correlated assets
                elif abs(symbol_corr) > 0.5:
                    stop_loss = volatility * 2.0  # Medium stop for moderately correlated assets
                else:
                    stop_loss = volatility * 2.5  # Wider stop for lowly correlated assets
                stop_loss_levels[symbol] = stop_loss
            
            stop_loss_df = pd.DataFrame.from_dict(
                stop_loss_levels,
                orient='index',
                columns=['Stop-Loss Level']
            )
            stop_loss_df['Stop-Loss Level'] = stop_loss_df['Stop-Loss Level'].apply(lambda x: f"{x:.2%}")
            st.dataframe(stop_loss_df)
        
        # Portfolio summary
        st.subheader("Portfolio Summary")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Value", f"${portfolio['total_value_usd']:,.2f}")
        col2.metric("24h Change", f"{portfolio['pnl_24h_pct']:.2f}%", 
                  f"{'+' if portfolio['pnl_24h_pct'] > 0 else ''}{portfolio['pnl_24h_pct']:.2f}%")
        col3.metric("7d Change", f"{portfolio['pnl_7d_pct']:.2f}%", 
                  f"{'+' if portfolio['pnl_7d_pct'] > 0 else ''}{portfolio['pnl_7d_pct']:.2f}%")
        col4.metric("30d Change", f"{portfolio['pnl_30d_pct']:.2f}%", 
                  f"{'+' if portfolio['pnl_30d_pct'] > 0 else ''}{portfolio['pnl_30d_pct']:.2f}%")
        
        # Portfolio composition
        st.subheader("Asset Allocation")
        
        # Create a dataframe with portfolio data
        portfolio_df = pd.DataFrame(portfolio['assets'])
        
        # Calculate percentage allocation
        portfolio_df['allocation'] = portfolio_df['value_usd'] / portfolio['total_value_usd'] * 100
        
        # Create a pie chart for asset allocation
        fig_pie = go.Figure(data=[go.Pie(
            labels=portfolio_df['symbol'],
            values=portfolio_df['value_usd'],
            hole=.4,
            marker_colors=['#1E88E5', '#5E35B1', '#43A047', '#FB8C00']
        )])
        
        fig_pie.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Active Trades
        st.subheader("Active Trades")
        
        if active_trades:
            # Create a dataframe with trades data
            trades_df = pd.DataFrame(active_trades)
            
            # Format the dataframe for display
            trades_df['timestamp'] = trades_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            trades_df['pnl_pct'] = trades_df['pnl_pct'].apply(lambda x: f"{x:.2f}%")
            trades_df['entry_price'] = trades_df['entry_price'].apply(lambda x: f"${x:,.2f}")
            trades_df['current_price'] = trades_df['current_price'].apply(lambda x: f"${x:,.2f}")
            
            # Display the trades with color coding for PnL
            def color_negative_red(val):
                try:
                    pnl = float(val.strip('%'))
                    color = 'red' if pnl < 0 else 'green'
                    return f'color: {color}'
                except:
                    return ''
            
            styled_df = trades_df.style.applymap(color_negative_red, subset=['pnl_pct'])
            st.dataframe(styled_df, hide_index=True)
        else:
            st.info("No active trades at the moment.")
        
        # Add correlation-based portfolio rebalancing triggers
        st.subheader("Correlation-Based Portfolio Rebalancing")
        
        if multi_data is not None:
            # Calculate returns and correlations
            returns = multi_data.pct_change()
            correlation_matrix = returns.corr()
            
            # Get current portfolio weights
            current_weights = {}
            for asset in portfolio['assets']:
                symbol = asset['symbol']
                if symbol != 'USDT':
                    current_weights[f"{symbol}/USDT"] = asset['value_usd'] / portfolio['total_value_usd']
            
            # Convert weights to numpy array
            weights_array = np.array([current_weights.get(symbol, 0) for symbol in returns.columns])
            
            # Detect correlation regime
            regime, regime_metrics = detect_correlation_regime(returns, correlation_matrix)
            
            # Display regime information
            st.markdown(f"**Current Correlation Regime:** {regime}")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Correlation Strength", f"{regime_metrics['correlation_strength']:.2f}")
            col2.metric("Correlation Stability", f"{regime_metrics['correlation_stability']:.2f}")
            col3.metric("Correlation Trend", f"{regime_metrics['correlation_trend']:+.2f}")
            
            # Find arbitrage opportunities
            st.markdown("**Correlation-Based Arbitrage Opportunities:**")
            opportunities = find_arbitrage_opportunities(returns, correlation_matrix, multi_data)
            
            if opportunities:
                for opp in opportunities:
                    st.info(f"**{opp['pair']}** - Correlation: {opp['correlation']:.2f}, "
                           f"Price Deviation: {opp['deviation']:+.2%}")
            else:
                st.info("No significant arbitrage opportunities detected at the moment.")
            
            # Calculate risk-adjusted metrics
            st.markdown("**Risk-Adjusted Performance Metrics:**")
            metrics = calculate_risk_adjusted_metrics(returns, correlation_matrix, weights_array)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            col2.metric("Sortino Ratio", f"{metrics['sortino_ratio']:.2f}")
            col3.metric("Information Ratio", f"{metrics['information_ratio']:.2f}")
            col4.metric("Correlation-Adjusted Return", f"{metrics['correlation_adjusted_return']:.2%}")
            
            # Perform stress testing
            st.markdown("**Portfolio Stress Testing:**")
            stress_metrics = stress_test_portfolio(returns, correlation_matrix, weights_array)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("VaR (95%)", f"{stress_metrics['var_95']:.2%}")
            col2.metric("CVaR (95%)", f"{stress_metrics['cvar_95']:.2%}")
            col3.metric("Max Loss", f"{stress_metrics['max_loss']:.2%}")
            col4.metric("Correlation Impact", f"{stress_metrics['correlation_impact']:.2f}")
            
            # Generate hedging suggestions
            st.markdown("**Hedging Suggestions:**")
            suggestions = generate_hedging_suggestions(returns, correlation_matrix, weights_array)
            
            if suggestions:
                for suggestion in suggestions:
                    st.info(f"**{suggestion['symbol']}** - {suggestion['suggestion']}")
            else:
                st.info("No hedging suggestions at the moment.")
        
        # Auto-refresh functionality
        if auto_refresh:
            time.sleep(refresh_interval)
            st.experimental_rerun()
            
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        st.error("An error occurred while loading the dashboard. Please try again later.")

if __name__ == "__main__":
    # For testing the page individually
    show({}) 