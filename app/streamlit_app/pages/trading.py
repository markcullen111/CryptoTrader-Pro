import streamlit as st
import asyncio
import pandas as pd
from app.utils.logger import setup_logger
from app.trading.exchange_client import ExchangeClient
from app.trading.strategy_manager import StrategyManager
from app.analytics.performance_analytics import PerformanceAnalytics

logger = setup_logger(__name__)

@st.cache_resource
def get_exchange_client():
    """Get or create exchange client instance."""
    return ExchangeClient()

@st.cache_resource
def get_strategy_manager():
    """Get or create strategy manager instance."""
    return StrategyManager()

@st.cache_resource
def get_performance_analytics():
    """Get or create performance analytics instance."""
    return PerformanceAnalytics()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_market_data(symbol: str, timeframe: str):
    """Get market data for the specified symbol and timeframe."""
    try:
        exchange_client = get_exchange_client()
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        data = loop.run_until_complete(exchange_client.get_ohlcv(symbol, timeframe))
        loop.close()
        
        # Convert to DataFrame for serialization
        if data is not None:
            return pd.DataFrame(data).to_dict(orient='records')
        return None
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return None

def display_trading_page():
    """Display the trading page."""
    try:
        st.title("Trading Dashboard")
        
        # Get instances
        exchange_client = get_exchange_client()
        strategy_manager = get_strategy_manager()
        performance_analytics = get_performance_analytics()
        
        # Sidebar controls
        with st.sidebar:
            st.header("Trading Controls")
            symbol = st.selectbox("Trading Pair", ["BTC/USDT", "ETH/USDT"])
            timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d"])
            
            if st.button("Refresh Data"):
                st.cache_data.clear()
        
        # Main content
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Market Data")
            market_data = get_market_data(symbol, timeframe)
            if market_data is not None:
                df = pd.DataFrame(market_data)
                st.line_chart(df)
            else:
                st.error("Failed to fetch market data")
        
        with col2:
            st.subheader("Active Strategies")
            strategies = strategy_manager.get_active_strategies()
            for strategy in strategies:
                st.write(f"- {strategy['name']} ({strategy['status']})")
        
        # Performance metrics
        st.subheader("Performance Metrics")
        metrics = performance_analytics.get_performance_metrics()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Return", f"{metrics['total_return']:.2%}")
        with col2:
            st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
        with col3:
            st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
            
    except Exception as e:
        logger.error(f"Error displaying trading page: {str(e)}")
        st.error("An error occurred while loading the trading page. Please try again later.")

if __name__ == "__main__":
    display_trading_page() 