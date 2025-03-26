import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from app.trading.trade_manager import TradeManager
from app.trading.exchange_client import ExchangeClient

logger = logging.getLogger(__name__)

@st.cache_resource(ttl=300)  # Cache for 5 minutes
def get_trade_manager():
    """Get trade manager instance."""
    return TradeManager()

@st.cache_resource(ttl=300)
def get_exchange_client():
    """Get exchange client instance."""
    return ExchangeClient()

@st.cache_data(ttl=300)
def get_trade_history(start_date=None, end_date=None, symbol=None):
    """Get trade history with optional filters."""
    try:
        trade_manager = get_trade_manager()
        trades = trade_manager.get_trade_history(start_date, end_date, symbol)
        return trades
    except Exception as e:
        logger.error(f"Error getting trade history: {e}")
        return None

@st.cache_data(ttl=300)
def calculate_trade_metrics(trades_df):
    """Calculate trading metrics from trades DataFrame."""
    if trades_df is None or trades_df.empty:
        return None
        
    try:
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # PnL metrics
        total_pnl = trades_df['pnl'].sum()
        avg_pnl = trades_df['pnl'].mean()
        max_pnl = trades_df['pnl'].max()
        min_pnl = trades_df['pnl'].min()
        
        # Risk metrics
        avg_risk = trades_df['risk'].mean()
        max_risk = trades_df['risk'].max()
        risk_reward_ratio = abs(avg_pnl / avg_risk) if avg_risk != 0 else 0
        
        # Time-based metrics
        avg_duration = trades_df['duration'].mean()
        max_duration = trades_df['duration'].max()
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'max_pnl': max_pnl,
            'min_pnl': min_pnl,
            'avg_risk': avg_risk,
            'max_risk': max_risk,
            'risk_reward_ratio': risk_reward_ratio,
            'avg_duration': avg_duration,
            'max_duration': max_duration
        }
    except Exception as e:
        logger.error(f"Error calculating trade metrics: {e}")
        return None

def show():
    """Display the Trading History page."""
    st.title("Trading History")
    
    # Check if the app is initialized
    if not st.session_state.get('initialized', False):
        st.warning("Please configure API credentials in Settings")
        return
    
    try:
        # Get exchange client for symbol list
        exchange_client = get_exchange_client()
        available_symbols = exchange_client.get_available_symbols()
        
        # Filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                datetime.now() - timedelta(days=30),
                max_value=datetime.now()
            )
            
        with col2:
            end_date = st.date_input(
                "End Date",
                datetime.now(),
                max_value=datetime.now()
            )
            
        with col3:
            selected_symbol = st.selectbox(
                "Symbol",
                ["All"] + available_symbols,
                index=0
            )
        
        # Get trade history
        trades = get_trade_history(
            start_date=start_date,
            end_date=end_date,
            symbol=selected_symbol if selected_symbol != "All" else None
        )
        
        if trades is None:
            st.error("Failed to load trade history")
            return
            
        # Convert to DataFrame
        df_trades = pd.DataFrame(trades)
        
        # Calculate metrics
        metrics = calculate_trade_metrics(df_trades)
        if metrics is None:
            st.error("Failed to calculate trade metrics")
            return
        
        # Display metrics
        st.subheader("Trading Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", metrics['total_trades'])
            st.metric("Win Rate", f"{metrics['win_rate']:.1%}")
            st.metric("Total PnL", f"${metrics['total_pnl']:,.2f}")
            
        with col2:
            st.metric("Winning Trades", metrics['winning_trades'])
            st.metric("Average PnL", f"${metrics['avg_pnl']:,.2f}")
            st.metric("Max PnL", f"${metrics['max_pnl']:,.2f}")
            
        with col3:
            st.metric("Losing Trades", metrics['losing_trades'])
            st.metric("Average Risk", f"${metrics['avg_risk']:,.2f}")
            st.metric("Min PnL", f"${metrics['min_pnl']:,.2f}")
            
        with col4:
            st.metric("Risk/Reward", f"{metrics['risk_reward_ratio']:.2f}")
            st.metric("Avg Duration", f"{metrics['avg_duration']:.1f}m")
            st.metric("Max Duration", f"{metrics['max_duration']:.1f}m")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Trade List", "Performance Analysis", "Export"])
        
        with tab1:
            # Trade list with filtering
            st.subheader("Trade List")
            
            # Additional filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                min_pnl = st.number_input(
                    "Min PnL",
                    value=float(df_trades['pnl'].min()),
                    step=10.0
                )
                
            with col2:
                max_pnl = st.number_input(
                    "Max PnL",
                    value=float(df_trades['pnl'].max()),
                    step=10.0
                )
                
            with col3:
                trade_type = st.selectbox(
                    "Trade Type",
                    ["All", "Long", "Short"],
                    index=0
                )
            
            # Filter DataFrame
            filtered_df = df_trades[
                (df_trades['pnl'] >= min_pnl) &
                (df_trades['pnl'] <= max_pnl)
            ]
            
            if trade_type != "All":
                filtered_df = filtered_df[filtered_df['type'] == trade_type]
            
            # Display filtered trades
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )
        
        with tab2:
            # Performance analysis
            st.subheader("Performance Analysis")
            
            # PnL over time
            fig_pnl = go.Figure()
            fig_pnl.add_trace(go.Scatter(
                x=df_trades['timestamp'],
                y=df_trades['pnl'].cumsum(),
                mode='lines',
                name='Cumulative PnL'
            ))
            
            fig_pnl.update_layout(
                title='Cumulative PnL Over Time',
                xaxis_title='Time',
                yaxis_title='Cumulative PnL ($)',
                height=400
            )
            
            st.plotly_chart(fig_pnl, use_container_width=True)
            
            # Win rate by symbol
            win_rate_by_symbol = df_trades.groupby('symbol').apply(
                lambda x: len(x[x['pnl'] > 0]) / len(x)
            ).reset_index()
            win_rate_by_symbol.columns = ['Symbol', 'Win Rate']
            
            fig_win = px.bar(
                win_rate_by_symbol,
                x='Symbol',
                y='Win Rate',
                title='Win Rate by Symbol'
            )
            
            st.plotly_chart(fig_win, use_container_width=True)
            
            # PnL distribution
            fig_dist = px.histogram(
                df_trades,
                x='pnl',
                title='PnL Distribution',
                nbins=50
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Risk vs Reward scatter plot
            fig_risk = px.scatter(
                df_trades,
                x='risk',
                y='pnl',
                color='type',
                title='Risk vs Reward'
            )
            
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with tab3:
            # Export functionality
            st.subheader("Export Trade History")
            
            col1, col2 = st.columns(2)
            
            with col1:
                export_format = st.selectbox(
                    "Export Format",
                    ["CSV", "Excel", "JSON"],
                    index=0
                )
                
            with col2:
                include_metrics = st.checkbox(
                    "Include Summary Metrics",
                    value=True
                )
            
            if st.button("Export Data"):
                try:
                    # Prepare export data
                    export_data = filtered_df.copy()
                    
                    if include_metrics:
                        # Add metrics to export
                        metrics_df = pd.DataFrame([metrics])
                        export_data = pd.concat([metrics_df, export_data])
                    
                    # Export based on format
                    if export_format == "CSV":
                        csv = export_data.to_csv(index=False)
                        st.download_button(
                            "Download CSV",
                            csv,
                            "trade_history.csv",
                            "text/csv"
                        )
                    elif export_format == "Excel":
                        excel = export_data.to_excel(index=False)
                        st.download_button(
                            "Download Excel",
                            excel,
                            "trade_history.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:  # JSON
                        json = export_data.to_json(orient='records')
                        st.download_button(
                            "Download JSON",
                            json,
                            "trade_history.json",
                            "application/json"
                        )
                        
                except Exception as e:
                    logger.error(f"Error exporting trade history: {e}")
                    st.error(f"An error occurred while exporting data: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error displaying Trading History page: {e}")
        st.error(f"An error occurred while loading the Trading History page: {str(e)}")

if __name__ == "__main__":
    # For testing the page individually
    show() 