import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from app.config.config_manager import ConfigManager
from app.trading.exchange_client import ExchangeClient

logger = logging.getLogger(__name__)

@st.cache_resource(ttl=300)  # Cache for 5 minutes
def get_config_manager():
    """Get config manager instance."""
    return ConfigManager()

@st.cache_resource(ttl=300)
def get_exchange_client():
    """Get exchange client instance."""
    return ExchangeClient()

@st.cache_data(ttl=300)
def get_exchange_info():
    """Get exchange information and supported features."""
    try:
        exchange_client = get_exchange_client()
        info = exchange_client.get_exchange_info()
        return info
    except Exception as e:
        logger.error(f"Error getting exchange info: {e}")
        return None

def show():
    """Display the Settings page."""
    st.title("Settings")
    
    try:
        # Get config manager
        config_manager = get_config_manager()
        
        # Create tabs for different settings
        tab1, tab2, tab3 = st.tabs(["API Configuration", "Trading Settings", "System Settings"])
        
        with tab1:
            # API Configuration
            st.subheader("API Configuration")
            
            # Get current API config
            api_config = config_manager.get_api_config()
            if api_config is None:
                st.error("Failed to load API configuration")
                return
            
            # Exchange selection
            exchange = st.selectbox(
                "Exchange",
                ["Binance", "Coinbase", "Kraken", "Kucoin"],
                index=["Binance", "Coinbase", "Kraken", "Kucoin"].index(api_config.get('exchange', 'Binance'))
            )
            
            # API credentials
            st.write("### API Credentials")
            
            col1, col2 = st.columns(2)
            
            with col1:
                api_key = st.text_input(
                    "API Key",
                    value=api_config.get('api_key', ''),
                    type="password"
                )
                
            with col2:
                api_secret = st.text_input(
                    "API Secret",
                    value=api_config.get('api_secret', ''),
                    type="password"
                )
            
            # Test connection
            if st.button("Test Connection", type="primary"):
                try:
                    exchange_client = get_exchange_client()
                    if exchange_client.test_connection():
                        st.success("API connection successful!")
                    else:
                        st.error("API connection failed")
                except Exception as e:
                    logger.error(f"Error testing API connection: {e}")
                    st.error(f"An error occurred while testing connection: {str(e)}")
            
            # Save API config
            if st.button("Save API Configuration"):
                try:
                    new_api_config = {
                        'exchange': exchange,
                        'api_key': api_key,
                        'api_secret': api_secret
                    }
                    config_manager.update_api_config(new_api_config)
                    st.success("API configuration saved successfully!")
                except Exception as e:
                    logger.error(f"Error saving API configuration: {e}")
                    st.error(f"An error occurred while saving configuration: {str(e)}")
        
        with tab2:
            # Trading Settings
            st.subheader("Trading Settings")
            
            # Get current trading config
            trading_config = config_manager.get_trading_config()
            if trading_config is None:
                st.error("Failed to load trading configuration")
                return
            
            # Trading pairs
            st.write("### Trading Pairs")
            
            exchange_info = get_exchange_info()
            if exchange_info:
                available_pairs = exchange_info.get('trading_pairs', [])
                selected_pairs = st.multiselect(
                    "Select Trading Pairs",
                    available_pairs,
                    default=trading_config.get('trading_pairs', [])
                )
            else:
                st.warning("Unable to load trading pairs. Please check API configuration.")
                selected_pairs = trading_config.get('trading_pairs', [])
            
            # Position sizing
            st.write("### Position Sizing")
            
            col1, col2 = st.columns(2)
            
            with col1:
                trading_config['position_size'] = st.number_input(
                    "Position Size (%)",
                    min_value=0.1,
                    max_value=100.0,
                    value=float(trading_config.get('position_size', 1.0)),
                    step=0.1
                )
                
                trading_config['max_positions'] = st.number_input(
                    "Max Positions",
                    min_value=1,
                    max_value=10,
                    value=int(trading_config.get('max_positions', 3)),
                    step=1
                )
                
            with col2:
                trading_config['leverage'] = st.number_input(
                    "Leverage",
                    min_value=1,
                    max_value=100,
                    value=int(trading_config.get('leverage', 1)),
                    step=1
                )
                
                trading_config['margin_type'] = st.selectbox(
                    "Margin Type",
                    ["Isolated", "Cross"],
                    index=["Isolated", "Cross"].index(trading_config.get('margin_type', 'Isolated'))
                )
            
            # Risk management
            st.write("### Risk Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                trading_config['stop_loss'] = st.number_input(
                    "Stop Loss (%)",
                    min_value=0.1,
                    max_value=10.0,
                    value=float(trading_config.get('stop_loss', 2.0)),
                    step=0.1
                )
                
                trading_config['take_profit'] = st.number_input(
                    "Take Profit (%)",
                    min_value=0.1,
                    max_value=20.0,
                    value=float(trading_config.get('take_profit', 4.0)),
                    step=0.1
                )
                
            with col2:
                trading_config['trailing_stop'] = st.number_input(
                    "Trailing Stop (%)",
                    min_value=0.0,
                    max_value=5.0,
                    value=float(trading_config.get('trailing_stop', 1.0)),
                    step=0.1
                )
                
                trading_config['max_drawdown'] = st.number_input(
                    "Max Drawdown (%)",
                    min_value=1.0,
                    max_value=50.0,
                    value=float(trading_config.get('max_drawdown', 20.0)),
                    step=1.0
                )
            
            # Save trading config
            if st.button("Save Trading Settings"):
                try:
                    trading_config['trading_pairs'] = selected_pairs
                    config_manager.update_trading_config(trading_config)
                    st.success("Trading settings saved successfully!")
                except Exception as e:
                    logger.error(f"Error saving trading settings: {e}")
                    st.error(f"An error occurred while saving settings: {str(e)}")
        
        with tab3:
            # System Settings
            st.subheader("System Settings")
            
            # Get current system config
            system_config = config_manager.get_system_config()
            if system_config is None:
                st.error("Failed to load system configuration")
                return
            
            # Logging settings
            st.write("### Logging Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                system_config['log_level'] = st.selectbox(
                    "Log Level",
                    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    index=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].index(
                        system_config.get('log_level', 'INFO')
                    )
                )
                
                system_config['log_to_file'] = st.checkbox(
                    "Log to File",
                    value=system_config.get('log_to_file', True)
                )
                
            with col2:
                system_config['log_retention_days'] = st.number_input(
                    "Log Retention (days)",
                    min_value=1,
                    max_value=90,
                    value=int(system_config.get('log_retention_days', 30)),
                    step=1
                )
                
                system_config['log_rotation_size'] = st.number_input(
                    "Log Rotation Size (MB)",
                    min_value=1,
                    max_value=1000,
                    value=int(system_config.get('log_rotation_size', 100)),
                    step=1
                )
            
            # Performance settings
            st.write("### Performance Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                system_config['cache_ttl'] = st.number_input(
                    "Cache TTL (minutes)",
                    min_value=1,
                    max_value=60,
                    value=int(system_config.get('cache_ttl', 5)),
                    step=1
                )
                
                system_config['max_workers'] = st.number_input(
                    "Max Workers",
                    min_value=1,
                    max_value=10,
                    value=int(system_config.get('max_workers', 4)),
                    step=1
                )
                
            with col2:
                system_config['update_interval'] = st.number_input(
                    "Update Interval (seconds)",
                    min_value=1,
                    max_value=60,
                    value=int(system_config.get('update_interval', 5)),
                    step=1
                )
                
                system_config['data_retention_days'] = st.number_input(
                    "Data Retention (days)",
                    min_value=1,
                    max_value=365,
                    value=int(system_config.get('data_retention_days', 90)),
                    step=1
                )
            
            # Save system config
            if st.button("Save System Settings"):
                try:
                    config_manager.update_system_config(system_config)
                    st.success("System settings saved successfully!")
                except Exception as e:
                    logger.error(f"Error saving system settings: {e}")
                    st.error(f"An error occurred while saving settings: {str(e)}")
            
            # System information
            st.write("### System Information")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("CPU Usage", f"{system_config.get('cpu_usage', 0):.1f}%")
                st.metric("Memory Usage", f"{system_config.get('memory_usage', 0):.1f}%")
                
            with col2:
                st.metric("Disk Usage", f"{system_config.get('disk_usage', 0):.1f}%")
                st.metric("Network Usage", f"{system_config.get('network_usage', 0):.1f} MB/s")
                
            with col3:
                st.metric("Uptime", system_config.get('uptime', '0:00:00'))
                st.metric("Last Update", system_config.get('last_update', 'Never'))
        
    except Exception as e:
        logger.error(f"Error displaying Settings page: {e}")
        st.error(f"An error occurred while loading the Settings page: {str(e)}")

if __name__ == "__main__":
    # For testing the page individually
    show() 