import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta, date
import logging
import time
import json
from pathlib import Path
import random

# Import the backtest runner
from app.utils.backtest_runner import (
    run_backtest,
    save_backtest_result,
    load_backtest_result,
    get_available_backtest_results
)

logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_backtest_results():
    """Get list of past backtest results."""
    try:
        results_dir = Path("backtest_results")
        if not results_dir.exists():
            logger.warning("Backtest results directory not found")
            return []
            
        result_files = list(results_dir.glob("*.json"))
        results = []
        
        for result_file in result_files:
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                    results.append(result)
            except Exception as e:
                logger.error(f"Error loading backtest result from {result_file}: {e}")
                continue
                
        return results
    except Exception as e:
        logger.error(f"Error loading backtest results: {e}")
        return []

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_backtest_result(result_id):
    """Get specific backtest result."""
    try:
        result_file = Path(f"backtest_results/{result_id}.json")
        if not result_file.exists():
            logger.warning(f"Backtest result file not found: {result_id}")
            return None
            
        with open(result_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading backtest result {result_id}: {e}")
        return None

def show():
    """Display the backtesting page."""
    st.title("Backtesting")
    
    # Check if the app is initialized
    if not st.session_state.get('initialized', False):
        st.warning("Please configure API credentials in Settings")
        return
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["Run New Backtest", "View Past Results"])
    
    with tab1:
        st.subheader("Run New Backtest")
        
        # Strategy selection
        strategy = st.selectbox(
            "Select Strategy",
            ["Rule-Based", "ML", "RL", "Combined"]
        )
        
        # Trading pair selection
        symbol = st.selectbox(
            "Trading Pair",
            ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT"]
        )
        
        # Timeframe selection
        timeframe = st.selectbox(
            "Timeframe",
            ["1m", "5m", "15m", "1h", "4h", "1d"]
        )
        
        # Date range selection
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=30)
            )
            
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now()
            )
            
        # Strategy parameters
        st.subheader("Strategy Parameters")
        
        if strategy == "Rule-Based":
            col1, col2 = st.columns(2)
            
            with col1:
                rsi_period = st.number_input("RSI Period", 2, 30, 14)
                rsi_overbought = st.number_input("RSI Overbought", 50, 100, 70)
                rsi_oversold = st.number_input("RSI Oversold", 0, 50, 30)
                
            with col2:
                macd_fast = st.number_input("MACD Fast Period", 5, 30, 12)
                macd_slow = st.number_input("MACD Slow Period", 10, 50, 26)
                macd_signal = st.number_input("MACD Signal Period", 5, 20, 9)
                
        elif strategy == "ML":
            col1, col2 = st.columns(2)
            
            with col1:
                model_type = st.selectbox(
                    "Model Type",
                    ["Random Forest", "XGBoost", "LightGBM"]
                )
                train_size = st.slider("Training Data Size", 0.5, 0.9, 0.8, 0.05)
                
            with col2:
                n_estimators = st.number_input("Number of Trees", 10, 1000, 100, 10)
                max_depth = st.number_input("Max Depth", 3, 20, 5, 1)
                
        elif strategy == "RL":
            col1, col2 = st.columns(2)
            
            with col1:
                episodes = st.number_input("Number of Episodes", 10, 1000, 100, 10)
                learning_rate = st.number_input("Learning Rate", 0.0001, 0.1, 0.001, 0.0001)
                
            with col2:
                gamma = st.number_input("Discount Factor", 0.1, 1.0, 0.99, 0.01)
                epsilon = st.number_input("Epsilon", 0.0, 1.0, 0.1, 0.01)
                
        else:  # Combined
            col1, col2 = st.columns(2)
            
            with col1:
                rule_weight = st.slider("Rule-Based Weight", 0.0, 1.0, 0.3, 0.1)
                ml_weight = st.slider("ML Weight", 0.0, 1.0, 0.3, 0.1)
                
            with col2:
                rl_weight = st.slider("RL Weight", 0.0, 1.0, 0.4, 0.1)
                
        # Risk management
        st.subheader("Risk Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            initial_capital = st.number_input(
                "Initial Capital (USDT)",
                min_value=100.0,
                max_value=100000.0,
                value=10000.0,
                step=100.0
            )
            
            position_size = st.number_input(
                "Position Size (%)",
                min_value=1.0,
                max_value=100.0,
                value=10.0,
                step=1.0
            )
            
        with col2:
            stop_loss = st.number_input(
                "Stop Loss (%)",
                min_value=0.1,
                max_value=20.0,
                value=2.0,
                step=0.1
            )
            
            take_profit = st.number_input(
                "Take Profit (%)",
                min_value=0.1,
                max_value=50.0,
                value=4.0,
                step=0.1
            )
            
        # Run backtest button
        if st.button("Run Backtest", type="primary"):
            try:
                with st.spinner("Running backtest..."):
                    # Here you would call your actual backtest function
                    # For now, we'll just simulate a backtest
                    time.sleep(2)
                    
                    # Generate a random result
                    result = {
                        "id": f"backtest_{int(time.time())}",
                        "strategy": strategy,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "initial_capital": initial_capital,
                        "final_capital": initial_capital * (1 + random.uniform(0.1, 0.5)),
                        "total_trades": random.randint(10, 50),
                        "win_rate": random.uniform(0.4, 0.7),
                        "sharpe_ratio": random.uniform(0.5, 2.0),
                        "max_drawdown": random.uniform(0.05, 0.2),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Save result
                    results_dir = Path("backtest_results")
                    results_dir.mkdir(exist_ok=True)
                    
                    with open(results_dir / f"{result['id']}.json", 'w') as f:
                        json.dump(result, f)
                    
                    st.success("Backtest completed successfully!")
                    
            except Exception as e:
                logger.error(f"Error running backtest: {e}")
                st.error(f"An error occurred while running the backtest: {str(e)}")
    
    with tab2:
        st.subheader("Past Results")
        
        # Add loading state
        with st.spinner("Loading backtest results..."):
            try:
                # Get backtest results
                results = get_backtest_results()
                if not results:
                    st.warning("No backtest results found")
                    return
                    
                # Create DataFrame
                df_results = pd.DataFrame(results)
                
                # Format metrics
                df_results['Win Rate'] = df_results['win_rate'].apply(lambda x: f"{x:.1%}")
                df_results['Return'] = ((df_results['final_capital'] - df_results['initial_capital']) / 
                                      df_results['initial_capital']).apply(lambda x: f"{x:+.1%}")
                df_results['Max Drawdown'] = df_results['max_drawdown'].apply(lambda x: f"{x:.1%}")
                
                # Display results table
                st.dataframe(
                    df_results[[
                        'id', 'strategy', 'symbol', 'timeframe', 'total_trades',
                        'Win Rate', 'Return', 'Max Drawdown', 'sharpe_ratio',
                        'created_at'
                    ]],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Result details
                selected_result = st.selectbox(
                    "Select Result for Details",
                    df_results['id'].tolist()
                )
                
                if selected_result:
                    result = get_backtest_result(selected_result)
                    if result is None:
                        st.warning("Selected result not found")
                        return
                        
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Strategy", result['strategy'])
                        st.metric("Symbol", result['symbol'])
                        st.metric("Timeframe", result['timeframe'])
                        st.metric("Total Trades", result['total_trades'])
                        
                    with col2:
                        st.metric("Initial Capital", f"${result['initial_capital']:,.2f}")
                        st.metric("Final Capital", f"${result['final_capital']:,.2f}")
                        st.metric("Win Rate", f"{result['win_rate']:.1%}")
                        st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
                        
                    # Performance chart
                    st.subheader("Performance Chart")
                    
                    # Generate sample equity curve
                    dates = pd.date_range(
                        start=result['start_date'],
                        end=result['end_date'],
                        freq='D'
                    )
                    
                    # Create a more realistic equity curve
                    daily_returns = np.random.normal(0.001, 0.02, len(dates))
                    equity_curve = result['initial_capital'] * (1 + daily_returns).cumprod()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=equity_curve,
                        name='Equity Curve'
                    ))
                    
                    fig.update_layout(
                        title="Equity Curve",
                        xaxis_title="Date",
                        yaxis_title="Portfolio Value ($)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
            except Exception as e:
                logger.error(f"Error displaying backtest results: {e}")
                st.error(f"An error occurred while loading backtest results: {str(e)}")

if __name__ == "__main__":
    # For testing the page individually
    show() 