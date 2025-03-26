import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from app.trading.exchange_client import ExchangeClient
from app.trading.trade_manager import TradeManager
from app.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

@st.cache_resource(ttl=300)  # Cache for 5 minutes
def get_exchange_client():
    """Get exchange client instance."""
    return ExchangeClient()

@st.cache_resource(ttl=300)
def get_trade_manager():
    """Get trade manager instance."""
    return TradeManager()

@st.cache_resource(ttl=300)
def get_config_manager():
    """Get config manager instance."""
    return ConfigManager()

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_market_data(symbol='BTC/USDT', timeframe='1h', limit=100):
    """Get market data with caching."""
    try:
        exchange_client = get_exchange_client()
        df = exchange_client.get_historical_data(symbol, timeframe, limit)
        if df is not None:
            # Convert DataFrame to a serializable format
            return {
                'data': df.to_dict(orient='records'),
                'columns': df.columns.tolist(),
                'index': df.index.tolist()
            }
        return None
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return None

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_order_book(symbol='BTC/USDT', limit=20):
    """Get order book with caching."""
    try:
        exchange_client = get_exchange_client()
        order_book = exchange_client.get_order_book(symbol, limit)
        if order_book is not None:
            # Convert order book to a serializable format
            return {
                'bids': order_book['bids'].tolist(),
                'asks': order_book['asks'].tolist()
            }
        return None
    except Exception as e:
        logger.error(f"Error getting order book: {e}")
        return None

def show():
    """Display the Trading page."""
    st.title("Trading")
    
    try:
        # Get managers
        exchange_client = get_exchange_client()
        trade_manager = get_trade_manager()
        config_manager = get_config_manager()
        
        # Get trading config
        trading_config = config_manager.get_trading_config()
        if trading_config is None:
            st.error("Failed to load trading configuration")
            return
        
        # Trading pair selection
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.selectbox(
                "Trading Pair",
                trading_config.get('trading_pairs', ['BTC/USDT']),
                index=0
            )
            
        with col2:
            timeframe = st.selectbox(
                "Timeframe",
                ["1m", "5m", "15m", "1h", "4h", "1d"],
                index=3
            )
        
        # Market data
        st.subheader("Market Data")
        
        market_data = get_market_data(symbol, timeframe)
        if market_data is None:
            st.error("Failed to load market data")
            return
        
        # Convert back to DataFrame
        df = pd.DataFrame(market_data['data'])
        df.index = pd.to_datetime(market_data['index'])
        
        # Price chart
        fig_price = go.Figure()
        fig_price.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ))
        
        fig_price.update_layout(
            title=f"{symbol} Price Chart",
            yaxis_title="Price",
            height=400
        )
        
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Order book
        st.subheader("Order Book")
        
        order_book = get_order_book(symbol)
        if order_book is None:
            st.error("Failed to load order book")
            return
        
        # Create order book visualization
        bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'amount'])
        asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'amount'])
        
        fig_ob = go.Figure()
        
        fig_ob.add_trace(go.Scatter(
            x=bids_df['price'],
            y=bids_df['amount'].cumsum(),
            name='Bids',
            line=dict(color='green')
        ))
        
        fig_ob.add_trace(go.Scatter(
            x=asks_df['price'],
            y=asks_df['amount'].cumsum(),
            name='Asks',
            line=dict(color='red')
        ))
        
        fig_ob.update_layout(
            title="Order Book",
            xaxis_title="Price",
            yaxis_title="Cumulative Amount",
            height=300
        )
        
        st.plotly_chart(fig_ob, use_container_width=True)
        
        # Trading controls
        st.subheader("Trading Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            order_type = st.selectbox(
                "Order Type",
                ["Market", "Limit", "Stop Loss", "Take Profit"]
            )
            
            side = st.selectbox(
                "Side",
                ["Buy", "Sell"]
            )
            
        with col2:
            amount = st.number_input(
                "Amount",
                min_value=0.0001,
                max_value=100.0,
                value=0.01,
                step=0.0001
            )
            
            if order_type in ["Limit", "Stop Loss", "Take Profit"]:
                price = st.number_input(
                    "Price",
                    min_value=0.0,
                    max_value=1000000.0,
                    value=float(df['close'].iloc[-1]),
                    step=0.1
                )
        
        # Place order button
        if st.button("Place Order", type="primary"):
            try:
                # Validate order
                if amount <= 0:
                    st.error("Amount must be greater than 0")
                    return
                
                if order_type in ["Limit", "Stop Loss", "Take Profit"] and price <= 0:
                    st.error("Price must be greater than 0")
                    return
                
                # Create order
                order = {
                    'symbol': symbol,
                    'type': order_type.lower(),
                    'side': side.lower(),
                    'amount': amount,
                    'price': price if order_type != "Market" else None
                }
                
                # Place order
                result = trade_manager.place_order(order)
                
                if result:
                    st.success("Order placed successfully!")
                else:
                    st.error("Failed to place order")
                    
            except Exception as e:
                logger.error(f"Error placing order: {e}")
                st.error(f"An error occurred while placing the order: {str(e)}")
        
        # Active orders
        st.subheader("Active Orders")
        
        active_orders = trade_manager.get_active_orders(symbol)
        if active_orders:
            df_orders = pd.DataFrame(active_orders)
            st.dataframe(df_orders, use_container_width=True)
            
            # Cancel order button
            if not df_orders.empty:
                order_to_cancel = st.selectbox(
                    "Select Order to Cancel",
                    df_orders['id'].tolist()
                )
                
                if st.button("Cancel Order"):
                    try:
                        if trade_manager.cancel_order(order_to_cancel):
                            st.success("Order cancelled successfully!")
                        else:
                            st.error("Failed to cancel order")
                    except Exception as e:
                        logger.error(f"Error cancelling order: {e}")
                        st.error(f"An error occurred while cancelling the order: {str(e)}")
        else:
            st.info("No active orders")
        
    except Exception as e:
        logger.error(f"Error displaying Trading page: {e}")
        st.error(f"An error occurred while loading the Trading page: {str(e)}")

if __name__ == "__main__":
    # For testing the page individually
    show() 