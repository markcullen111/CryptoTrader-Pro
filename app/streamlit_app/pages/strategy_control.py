import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from app.trading.strategy_manager import StrategyManager
from app.trading.exchange_client import ExchangeClient
from app.ml.model_manager import ModelManager
import time

# Use flexible import approach for the api module
try:
    # Try first as absolute import from app structure
    from app.streamlit_app.api import *
except ImportError:
    try:
        # Try as relative import
        import sys
        from pathlib import Path
        
        # Add parent directory to path
        parent_dir = str(Path(__file__).parent.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Import API module
        from api import *
    except ImportError as e:
        st.error(f"Error importing API module: {e}")

logger = logging.getLogger(__name__)

@st.cache_resource(ttl=300)  # Cache for 5 minutes
def get_strategy_manager():
    """Get strategy manager instance."""
    return StrategyManager()

@st.cache_resource(ttl=300)
def get_exchange_client():
    """Get exchange client instance."""
    return ExchangeClient()

@st.cache_resource(ttl=300)
def get_model_manager():
    """Get model manager instance."""
    return ModelManager()

@st.cache_data(ttl=300)
def get_strategies():
    """Get list of strategies."""
    try:
        strategy_manager = get_strategy_manager()
        return strategy_manager.get_strategies()
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return None

@st.cache_data(ttl=300)
def get_strategy_metrics(strategy_id):
    """Get strategy metrics."""
    try:
        strategy_manager = get_strategy_manager()
        return strategy_manager.get_strategy_metrics(strategy_id)
    except Exception as e:
        logger.error(f"Error getting strategy metrics: {e}")
        return None

@st.cache_data(ttl=300)
def get_strategy_performance(strategy_id):
    """Get strategy performance data."""
    try:
        strategy_manager = get_strategy_manager()
        return strategy_manager.get_strategy_performance(strategy_id)
    except Exception as e:
        logger.error(f"Error getting strategy performance: {e}")
        return None

@st.cache_data(ttl=300)
def get_strategy_comparison(strategy_ids):
    """Get strategy comparison metrics."""
    try:
        strategy_manager = get_strategy_manager()
        return strategy_manager.compare_strategies(strategy_ids)
    except Exception as e:
        logger.error(f"Error comparing strategies: {e}")
        return None

def show():
    """Display the Strategy Control page."""
    st.title("Strategy Control")
    
    # Check if the app is initialized
    if not st.session_state.get('initialized', False):
        st.warning("Please configure API credentials in Settings")
        return
    
    try:
        # Get strategy manager
        strategy_manager = get_strategy_manager()
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Strategy Management", "Performance Analysis", "Configuration", "Real-time Monitoring"])
        
        with tab1:
            # Strategy management
            st.subheader("Strategy Management")
            
            # Create new strategy
            with st.expander("Create New Strategy"):
                col1, col2 = st.columns(2)
                
                with col1:
                    strategy_name = st.text_input("Strategy Name")
                    description = st.text_area("Description")
                    
                with col2:
                    strategy_type = st.selectbox(
                        "Strategy Type",
                        ["Mean Reversion", "Trend Following", "Breakout", "ML-Based"]
                    )
                    
                    if strategy_type == "ML-Based":
                        # Get available models
                        model_manager = get_model_manager()
                        available_models = model_manager.get_models()
                        if available_models:
                            model_id = st.selectbox(
                                "Select ML Model",
                                [model['id'] for model in available_models],
                                format_func=lambda x: next((m['name'] for m in available_models if m['id'] == x), x)
                            )
                
                # Strategy parameters
                st.write("### Strategy Parameters")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    params = {}
                    params['timeframe'] = st.selectbox(
                        "Timeframe",
                        ["1m", "5m", "15m", "1h", "4h", "1d"]
                    )
                    
                    params['symbols'] = st.multiselect(
                        "Trading Pairs",
                        ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT"],
                        default=["BTC/USDT"]
                    )
                    
                with col2:
                    params['position_size'] = st.number_input(
                        "Position Size (%)",
                        min_value=0.1,
                        max_value=100.0,
                        value=1.0,
                        step=0.1
                    )
                    
                    params['max_positions'] = st.number_input(
                        "Max Positions",
                        min_value=1,
                        max_value=10,
                        value=3,
                        step=1
                    )
                
                # Risk management
                st.write("### Risk Management")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    risk_params = {}
                    risk_params['stop_loss'] = st.number_input(
                        "Stop Loss (%)",
                        min_value=0.1,
                        max_value=10.0,
                        value=2.0,
                        step=0.1
                    )
                    
                    risk_params['take_profit'] = st.number_input(
                        "Take Profit (%)",
                        min_value=0.1,
                        max_value=20.0,
                        value=4.0,
                        step=0.1
                    )
                    
                with col2:
                    risk_params['max_drawdown'] = st.number_input(
                        "Max Drawdown (%)",
                        min_value=1.0,
                        max_value=50.0,
                        value=10.0,
                        step=1.0
                    )
                    
                    risk_params['daily_loss_limit'] = st.number_input(
                        "Daily Loss Limit (%)",
                        min_value=1.0,
                        max_value=20.0,
                        value=5.0,
                        step=1.0
                    )
                
                # Advanced settings
                with st.expander("Advanced Settings"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        advanced_params = {}
                        advanced_params['use_trailing_stop'] = st.checkbox("Use Trailing Stop", value=True)
                        if advanced_params['use_trailing_stop']:
                            advanced_params['trailing_stop_distance'] = st.number_input(
                                "Trailing Stop Distance (%)",
                                min_value=0.1,
                                max_value=5.0,
                                value=1.0,
                                step=0.1
                            )
                        
                        advanced_params['use_dynamic_position_sizing'] = st.checkbox("Use Dynamic Position Sizing", value=False)
                        
                    with col2:
                        advanced_params['use_hedging'] = st.checkbox("Use Hedging", value=False)
                        if advanced_params['use_hedging']:
                            advanced_params['hedge_ratio'] = st.number_input(
                                "Hedge Ratio",
                                min_value=0.1,
                                max_value=1.0,
                                value=0.5,
                                step=0.1
                            )
                        
                        advanced_params['use_market_orders'] = st.checkbox("Use Market Orders", value=False)
                
                if st.button("Create Strategy", type="primary"):
                    try:
                        strategy_id = strategy_manager.create_strategy(
                            name=strategy_name,
                            description=description,
                            strategy_type=strategy_type,
                            params=params,
                            risk_params=risk_params,
                            advanced_params=advanced_params,
                            model_id=model_id if strategy_type == "ML-Based" else None
                        )
                        st.success(f"Strategy created successfully! ID: {strategy_id}")
                    except Exception as e:
                        logger.error(f"Error creating strategy: {e}")
                        st.error(f"An error occurred while creating the strategy: {str(e)}")
            
            # List strategies
            st.write("### Strategies")
            
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Status Filter",
                    ["All", "Active", "Inactive", "Paused", "Failed"],
                    index=0
                )
            
            with col2:
                type_filter = st.selectbox(
                    "Strategy Type Filter",
                    ["All", "Mean Reversion", "Trend Following", "Breakout", "ML-Based"],
                    index=0
                )
            
            with col3:
                date_filter = st.date_input(
                    "Date Range",
                    value=(datetime.now() - timedelta(days=30), datetime.now())
                )
            
            strategies = get_strategies()
            if strategies is None:
                st.error("Failed to load strategies")
                return
            
            # Filter strategies
            filtered_strategies = strategies
            if status_filter != "All":
                filtered_strategies = [strategy for strategy in filtered_strategies if strategy['status'] == status_filter.lower()]
            if type_filter != "All":
                filtered_strategies = [strategy for strategy in filtered_strategies if strategy['strategy_type'] == type_filter]
            filtered_strategies = [
                strategy for strategy in filtered_strategies 
                if datetime.strptime(strategy['created_at'], '%Y-%m-%d %H:%M:%S').date() >= date_filter[0]
                and datetime.strptime(strategy['created_at'], '%Y-%m-%d %H:%M:%S').date() <= date_filter[1]
            ]
            
            for strategy in filtered_strategies:
                with st.expander(f"{strategy['name']} - {strategy['status']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Description:**")
                        st.write(strategy['description'])
                        
                    with col2:
                        st.write("**Parameters:**")
                        for param, value in strategy['params'].items():
                            st.write(f"- {param}: {value}")
                            
                    with col3:
                        st.write("**Status:**")
                        st.write(f"- Created: {strategy['created_at']}")
                        st.write(f"- Status: {strategy['status']}")
                        st.write(f"- Type: {strategy['strategy_type']}")
                    
                    # Strategy controls
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if strategy['status'] == 'active':
                            if st.button("Stop", key=f"stop_{strategy['id']}"):
                                try:
                                    strategy_manager.stop_strategy(strategy['id'])
                                    st.success("Strategy stopped successfully!")
                                except Exception as e:
                                    logger.error(f"Error stopping strategy: {e}")
                                    st.error(f"An error occurred while stopping the strategy: {str(e)}")
                        else:
                            if st.button("Start", key=f"start_{strategy['id']}"):
                                try:
                                    strategy_manager.start_strategy(strategy['id'])
                                    st.success("Strategy started successfully!")
                                except Exception as e:
                                    logger.error(f"Error starting strategy: {e}")
                                    st.error(f"An error occurred while starting the strategy: {str(e)}")
                    
                    with col2:
                        if st.button("View Results", key=f"results_{strategy['id']}"):
                            st.session_state['selected_strategy'] = strategy['id']
                            st.experimental_rerun()
                    
                    with col3:
                        if st.button("Export", key=f"export_{strategy['id']}"):
                            try:
                                metrics = get_strategy_metrics(strategy['id'])
                                if metrics:
                                    df = pd.DataFrame(metrics)
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        "Download Metrics",
                                        csv,
                                        f"strategy_{strategy['id']}_metrics.csv",
                                        "text/csv"
                                    )
                            except Exception as e:
                                logger.error(f"Error exporting metrics: {e}")
                                st.error(f"An error occurred while exporting metrics: {str(e)}")
                    
                    with col4:
                        if st.button("Delete", key=f"delete_{strategy['id']}"):
                            try:
                                if strategy_manager.delete_strategy(strategy['id']):
                                    st.success("Strategy deleted successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to delete strategy")
                            except Exception as e:
                                logger.error(f"Error deleting strategy: {e}")
                                st.error(f"An error occurred while deleting the strategy: {str(e)}")
        
        with tab2:
            # Performance analysis
            st.subheader("Performance Analysis")
            
            # Get selected strategy
            selected_strategy = st.session_state.get('selected_strategy')
            if not selected_strategy:
                st.info("Select a strategy to view its performance analysis")
                return
            
            metrics = get_strategy_metrics(selected_strategy)
            if metrics is None:
                st.error("Failed to load strategy metrics")
                return
            
            # Convert metrics to DataFrame
            df_metrics = pd.DataFrame(metrics)
            
            # Performance metrics
            st.write("### Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Return", f"{df_metrics['total_return'].iloc[-1]:.2%}")
                st.metric("Win Rate", f"{df_metrics['win_rate'].iloc[-1]:.2%}")
                
            with col2:
                st.metric("Sharpe Ratio", f"{df_metrics['sharpe_ratio'].iloc[-1]:.2f}")
                st.metric("Max Drawdown", f"{df_metrics['max_drawdown'].iloc[-1]:.2%}")
                
            with col3:
                st.metric("Profit Factor", f"{df_metrics['profit_factor'].iloc[-1]:.2f}")
                st.metric("Total Trades", f"{df_metrics['total_trades'].iloc[-1]}")
                
            with col4:
                st.metric("Last Updated", df_metrics['timestamp'].iloc[-1])
                st.metric("Active Trades", f"{df_metrics['active_trades'].iloc[-1]}")
            
            # Performance visualizations
            st.write("### Performance Visualizations")
            
            # Equity curve
            performance = get_strategy_performance(selected_strategy)
            if performance:
                df_performance = pd.DataFrame(performance)
                
                fig_equity = go.Figure()
                
                fig_equity.add_trace(go.Scatter(
                    x=df_performance['timestamp'],
                    y=df_performance['equity'],
                    mode='lines',
                    name='Equity'
                ))
                
                fig_equity.update_layout(
                    title='Equity Curve',
                    xaxis_title='Time',
                    yaxis_title='Equity',
                    height=400
                )
                
                st.plotly_chart(fig_equity, use_container_width=True)
                
                # Drawdown
                fig_dd = go.Figure()
                
                fig_dd.add_trace(go.Scatter(
                    x=df_performance['timestamp'],
                    y=df_performance['drawdown'],
                    mode='lines',
                    name='Drawdown',
                    fill='tozeroy'
                ))
                
                fig_dd.update_layout(
                    title='Drawdown',
                    xaxis_title='Time',
                    yaxis_title='Drawdown (%)',
                    height=400
                )
                
                st.plotly_chart(fig_dd, use_container_width=True)
                
                # Monthly returns heatmap
                df_performance['month'] = pd.to_datetime(df_performance['timestamp']).dt.strftime('%Y-%m')
                monthly_returns = df_performance.groupby('month')['returns'].sum().unstack()
                
                fig_heatmap = px.imshow(
                    monthly_returns,
                    title='Monthly Returns Heatmap',
                    labels=dict(x="Month", y="Year", color="Returns")
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with tab3:
            # Configuration
            st.subheader("Strategy Configuration")
            
            if not selected_strategy:
                st.info("Select a strategy to view its configuration")
                return
            
            # Get strategy details
            strategy = next((s for s in strategies if s['id'] == selected_strategy), None)
            if not strategy:
                st.error("Strategy not found")
                return
            
            # Strategy parameters
            st.write("### Strategy Parameters")
            
            col1, col2 = st.columns(2)
            
            with col1:
                strategy['params']['timeframe'] = st.selectbox(
                    "Timeframe",
                    ["1m", "5m", "15m", "1h", "4h", "1d"],
                    index=["1m", "5m", "15m", "1h", "4h", "1d"].index(strategy['params']['timeframe'])
                )
                
                strategy['params']['symbols'] = st.multiselect(
                    "Trading Pairs",
                    ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT"],
                    default=strategy['params']['symbols']
                )
                
            with col2:
                strategy['params']['position_size'] = st.number_input(
                    "Position Size (%)",
                    min_value=0.1,
                    max_value=100.0,
                    value=float(strategy['params']['position_size']),
                    step=0.1
                )
                
                strategy['params']['max_positions'] = st.number_input(
                    "Max Positions",
                    min_value=1,
                    max_value=10,
                    value=int(strategy['params']['max_positions']),
                    step=1
                )
            
            # Risk management
            st.write("### Risk Management")
            
            col1, col2 = st.columns(2)
            
            with col1:
                strategy['risk_params']['stop_loss'] = st.number_input(
                    "Stop Loss (%)",
                    min_value=0.1,
                    max_value=10.0,
                    value=float(strategy['risk_params']['stop_loss']),
                    step=0.1
                )
                
                strategy['risk_params']['take_profit'] = st.number_input(
                    "Take Profit (%)",
                    min_value=0.1,
                    max_value=20.0,
                    value=float(strategy['risk_params']['take_profit']),
                    step=0.1
                )
                
            with col2:
                strategy['risk_params']['max_drawdown'] = st.number_input(
                    "Max Drawdown (%)",
                    min_value=1.0,
                    max_value=50.0,
                    value=float(strategy['risk_params']['max_drawdown']),
                    step=1.0
                )
                
                strategy['risk_params']['daily_loss_limit'] = st.number_input(
                    "Daily Loss Limit (%)",
                    min_value=1.0,
                    max_value=20.0,
                    value=float(strategy['risk_params']['daily_loss_limit']),
                    step=1.0
                )
            
            # Advanced settings
            with st.expander("Advanced Settings"):
                col1, col2 = st.columns(2)
                
                with col1:
                    strategy['advanced_params']['use_trailing_stop'] = st.checkbox(
                        "Use Trailing Stop",
                        value=strategy['advanced_params']['use_trailing_stop']
                    )
                    
                    if strategy['advanced_params']['use_trailing_stop']:
                        strategy['advanced_params']['trailing_stop_distance'] = st.number_input(
                            "Trailing Stop Distance (%)",
                            min_value=0.1,
                            max_value=5.0,
                            value=float(strategy['advanced_params']['trailing_stop_distance']),
                            step=0.1
                        )
                    
                    strategy['advanced_params']['use_dynamic_position_sizing'] = st.checkbox(
                        "Use Dynamic Position Sizing",
                        value=strategy['advanced_params']['use_dynamic_position_sizing']
                    )
                    
                with col2:
                    strategy['advanced_params']['use_hedging'] = st.checkbox(
                        "Use Hedging",
                        value=strategy['advanced_params']['use_hedging']
                    )
                    
                    if strategy['advanced_params']['use_hedging']:
                        strategy['advanced_params']['hedge_ratio'] = st.number_input(
                            "Hedge Ratio",
                            min_value=0.1,
                            max_value=1.0,
                            value=float(strategy['advanced_params']['hedge_ratio']),
                            step=0.1
                        )
                    
                    strategy['advanced_params']['use_market_orders'] = st.checkbox(
                        "Use Market Orders",
                        value=strategy['advanced_params']['use_market_orders']
                    )
            
            if st.button("Save Configuration", type="primary"):
                try:
                    if strategy_manager.update_strategy_config(selected_strategy, strategy):
                        st.success("Configuration updated successfully!")
                    else:
                        st.error("Failed to update configuration")
                except Exception as e:
                    logger.error(f"Error updating configuration: {e}")
                    st.error(f"An error occurred while updating the configuration: {str(e)}")
        
        with tab4:
            # Real-time monitoring
            st.subheader("Real-time Monitoring")
            
            if not selected_strategy:
                st.info("Select a strategy to view real-time monitoring")
                return
            
            # Get current strategy status
            strategy = next((s for s in strategies if s['id'] == selected_strategy), None)
            if not strategy:
                st.error("Strategy not found")
                return
            
            if strategy['status'] != 'active':
                st.warning("Strategy is not currently active")
                return
            
            # Real-time metrics
            st.write("### Current Performance")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Return",
                    f"{df_metrics['total_return'].iloc[-1]:.2%}"
                )
                
            with col2:
                st.metric(
                    "Active Trades",
                    f"{df_metrics['active_trades'].iloc[-1]}"
                )
                
            with col3:
                st.metric(
                    "Last Update",
                    f"{datetime.now() - datetime.strptime(df_metrics['timestamp'].iloc[-1], '%Y-%m-%d %H:%M:%S'):.1f}m ago"
                )
            
            # Real-time performance
            st.write("### Real-time Performance")
            
            if performance:
                df_performance = pd.DataFrame(performance)
                
                # Real-time equity curve
                fig_rt = go.Figure()
                
                fig_rt.add_trace(go.Scatter(
                    x=df_performance['timestamp'],
                    y=df_performance['equity'],
                    mode='lines',
                    name='Equity'
                ))
                
                fig_rt.update_layout(
                    title='Real-time Equity Curve',
                    xaxis_title='Time',
                    yaxis_title='Equity',
                    height=400
                )
                
                st.plotly_chart(fig_rt, use_container_width=True)
                
                # Real-time drawdown
                fig_rt_dd = go.Figure()
                
                fig_rt_dd.add_trace(go.Scatter(
                    x=df_performance['timestamp'],
                    y=df_performance['drawdown'],
                    mode='lines',
                    name='Drawdown',
                    fill='tozeroy'
                ))
                
                fig_rt_dd.update_layout(
                    title='Real-time Drawdown',
                    xaxis_title='Time',
                    yaxis_title='Drawdown (%)',
                    height=400
                )
                
                st.plotly_chart(fig_rt_dd, use_container_width=True)
            
            # Auto-refresh
            st.write("### Auto-refresh Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                auto_refresh = st.checkbox("Enable Auto-refresh", value=True)
                
            with col2:
                if auto_refresh:
                    refresh_interval = st.number_input(
                        "Refresh Interval (seconds)",
                        min_value=5,
                        max_value=60,
                        value=10,
                        step=5
                    )
            
            if auto_refresh:
                st.write(f"Next refresh in {refresh_interval} seconds...")
                time.sleep(refresh_interval)
                st.experimental_rerun()
        
    except Exception as e:
        logger.error(f"Error displaying Strategy Control page: {e}")
        st.error(f"An error occurred while loading the Strategy Control page: {str(e)}")

if __name__ == "__main__":
    # For testing the page individually
    show() 