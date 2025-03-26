import streamlit as st
import asyncio
import pandas as pd
from app.utils.logger import setup_logger
from app.trading.exchange_client import ExchangeClient
from app.trading.strategy_manager import StrategyManager
from app.analytics.performance_analytics import PerformanceAnalytics
from datetime import datetime

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

@st.cache_data
async def get_market_data():
    try:
        exchange_client = ExchangeClient()
        data = await exchange_client.get_market_data()
        # Convert to serializable format
        return {
            'symbols': list(data.keys()),
            'prices': {symbol: float(price) for symbol, price in data.items()},
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        st.error(f"Error fetching market data: {str(e)}")
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
            market_data = asyncio.run(get_market_data())
            if market_data:
                st.write("Current Market Prices:")
                for symbol, price in market_data['prices'].items():
                    st.write(f"{symbol}: ${price:,.2f}")
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