import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
import numpy as np
import logging

# Get logger
logger = logging.getLogger(__name__)

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

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import API module
from api import *

@st.cache_data(ttl=300)  # Cache for 5 minutes
def calculate_performance_metrics(trades_df):
    """Calculate performance metrics from trades data."""
    try:
        if trades_df.empty:
            return None
            
        # Calculate basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate PnL metrics
        total_pnl = trades_df['pnl'].sum()
        avg_pnl = trades_df['pnl'].mean()
        max_drawdown = calculate_max_drawdown(trades_df['cumulative_pnl'])
        
        # Calculate risk metrics
        returns = trades_df['pnl'].pct_change()
        sharpe_ratio = calculate_sharpe_ratio(returns)
        sortino_ratio = calculate_sortino_ratio(returns)
        
        # Calculate additional metrics
        profit_factor = abs(trades_df[trades_df['pnl'] > 0]['pnl'].sum() / 
                          trades_df[trades_df['pnl'] < 0]['pnl'].sum()) if len(trades_df[trades_df['pnl'] < 0]) > 0 else float('inf')
        
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if len(trades_df[trades_df['pnl'] > 0]) > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if len(trades_df[trades_df['pnl'] < 0]) > 0 else 0
        
        max_consecutive_wins = calculate_max_consecutive(trades_df['pnl'], True)
        max_consecutive_losses = calculate_max_consecutive(trades_df['pnl'], False)
        
        # Calculate recovery factor
        recovery_factor = total_pnl / max_drawdown if max_drawdown > 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'recovery_factor': recovery_factor
        }
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}")
        return None

@st.cache_data(ttl=300)
def calculate_max_drawdown(cumulative_pnl):
    """Calculate maximum drawdown from cumulative PnL."""
    try:
        rolling_max = cumulative_pnl.expanding().max()
        drawdowns = cumulative_pnl - rolling_max
        return abs(drawdowns.min())
    except Exception as e:
        logger.error(f"Error calculating max drawdown: {e}")
        return 0

@st.cache_data(ttl=300)
def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio from returns."""
    try:
        if len(returns) < 2:
            return 0
        excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    except Exception as e:
        logger.error(f"Error calculating Sharpe ratio: {e}")
        return 0

@st.cache_data(ttl=300)
def calculate_sortino_ratio(returns, risk_free_rate=0.02):
    """Calculate Sortino ratio from returns."""
    try:
        if len(returns) < 2:
            return 0
        excess_returns = returns - risk_free_rate/252
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()
    except Exception as e:
        logger.error(f"Error calculating Sortino ratio: {e}")
        return 0

@st.cache_data(ttl=300)
def calculate_max_consecutive(series, positive=True):
    """Calculate maximum consecutive wins or losses."""
    try:
        if positive:
            mask = series > 0
        else:
            mask = series < 0
            
        consecutive = mask.astype(int)
        consecutive = consecutive * (consecutive.groupby((consecutive != consecutive.shift()).cumsum()).cumsum())
        return consecutive.max()
    except Exception as e:
        logger.error(f"Error calculating max consecutive: {e}")
        return 0

def show():
    """Display the performance visualization page."""
    st.title("Performance Analysis")
    
    # Check if the app is initialized
    if not st.session_state.get('initialized', False):
        st.warning("Please configure API credentials in Settings")
        return
    
    # Time period selection
    time_periods = {
        "1 Week": 7,
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365,
        "All Time": 1000  # Just a large number
    }
    
    selected_period = st.selectbox(
        "Select Time Period",
        list(time_periods.keys()),
        index=2
    )
    
    days = time_periods[selected_period]
    
    # Add loading state
    with st.spinner("Loading performance data..."):
        try:
            # Get performance data
            performance_data = get_performance_data()
            if performance_data is None:
                st.error("Failed to load performance data")
                return
                
            # Convert to DataFrame if it's not already
            if not isinstance(performance_data, pd.DataFrame):
                performance_data = pd.DataFrame(performance_data)
                
            # Calculate metrics
            metrics = calculate_performance_metrics(performance_data)
            if metrics is None:
                st.error("Failed to calculate performance metrics")
                return
                
            # Display metrics in a grid
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trades", metrics['total_trades'])
                st.metric("Win Rate", f"{metrics['win_rate']:.1%}")
                st.metric("Total PnL", f"${metrics['total_pnl']:,.2f}")
                st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
                
            with col2:
                st.metric("Average PnL", f"${metrics['avg_pnl']:,.2f}")
                st.metric("Max Drawdown", f"${metrics['max_drawdown']:,.2f}")
                st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
                st.metric("Sortino Ratio", f"{metrics['sortino_ratio']:.2f}")
                
            with col3:
                st.metric("Average Win", f"${metrics['avg_win']:,.2f}")
                st.metric("Average Loss", f"${metrics['avg_loss']:,.2f}")
                st.metric("Max Consecutive Wins", metrics['max_consecutive_wins'])
                st.metric("Max Consecutive Losses", metrics['max_consecutive_losses'])
                
            with col4:
                st.metric("Recovery Factor", f"{metrics['recovery_factor']:.2f}")
                st.metric("Winning Trades", metrics['winning_trades'])
                st.metric("Losing Trades", metrics['losing_trades'])
                
            # Display performance charts
            st.subheader("Performance Charts")
            
            # Equity curve
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=performance_data.index,
                y=performance_data['cumulative_pnl'],
                name='Equity Curve'
            ))
            fig.update_layout(
                title='Equity Curve',
                xaxis_title='Date',
                yaxis_title='Cumulative PnL ($)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Drawdown chart
            fig = go.Figure()
            drawdown = (performance_data['cumulative_pnl'] - 
                       performance_data['cumulative_pnl'].expanding().max())
            fig.add_trace(go.Scatter(
                x=performance_data.index,
                y=drawdown,
                name='Drawdown',
                fill='tozeroy'
            ))
            fig.update_layout(
                title='Drawdown',
                xaxis_title='Date',
                yaxis_title='Drawdown ($)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Monthly returns heatmap
            st.subheader("Monthly Returns Heatmap")
            
            monthly_returns = performance_data['pnl'].resample('M').sum()
            monthly_returns = monthly_returns.pivot_table(
                index=monthly_returns.index.year,
                columns=monthly_returns.index.month,
                values='pnl',
                aggfunc='sum'
            )
            
            fig = go.Figure(data=go.Heatmap(
                z=monthly_returns.values,
                x=monthly_returns.columns,
                y=monthly_returns.index,
                colorscale='RdYlGn',
                text=np.round(monthly_returns.values, 2),
                texttemplate='%{text}%',
                textfont={"size": 10}
            ))
            
            fig.update_layout(
                title='Monthly Returns Heatmap',
                xaxis_title='Month',
                yaxis_title='Year',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trade distribution
            st.subheader("Trade Distribution")
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=performance_data['pnl'],
                name='Trade PnL Distribution',
                nbinsx=50
            ))
            
            fig.update_layout(
                title='Trade PnL Distribution',
                xaxis_title='PnL ($)',
                yaxis_title='Count',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Error displaying performance page: {e}")
            st.error(f"An error occurred while loading the performance page: {str(e)}")
    
    # Trade analysis
    st.subheader("Trade Analysis")
    
    # Create tabs for different trade visualizations
    tab1, tab2 = st.tabs(["Trade Outcomes", "Strategy Performance"])
    
    with tab1:
        # Trade outcomes analysis
        try:
            # Get trade outcomes data
            trade_outcomes = get_trade_outcomes()
            if trade_outcomes is None:
                st.warning("No trade outcomes data available")
                return
                
            df_trades = pd.DataFrame(trade_outcomes)
            
            # Create win/loss chart
            fig = px.histogram(
                df_trades,
                x='Strategy',
                color='Outcome',
                barmode='group',
                title='Win/Loss Count by Strategy',
                category_orders={"Outcome": ["Win", "Loss"]}
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Average return by strategy
            avg_returns = df_trades.groupby(['Strategy', 'Outcome'])['Return'].mean().reset_index()
            
            fig = px.bar(
                avg_returns,
                x='Strategy',
                y='Return',
                color='Outcome',
                title='Average Return per Trade (%)',
                barmode='group',
                text_auto='.1f'
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Error displaying trade outcomes: {e}")
            st.error(f"An error occurred while displaying trade outcomes: {str(e)}")
    
    with tab2:
        # Strategy performance metrics
        try:
            # Get strategy performance data
            strategy_performance = get_strategy_performance()
            if strategy_performance is None:
                st.warning("No strategy performance data available")
                return
                
            df_performance = pd.DataFrame(strategy_performance)
            
            # Create performance table
            st.dataframe(df_performance, use_container_width=True)
            
            # Create radar chart for strategy comparison
            radar_metrics = ['Win Rate (%)', 'Avg Win (%)', 'Avg Loss (%)', 'Profit Factor', 'Sharpe Ratio']
            df_radar = df_performance[df_performance['Metric'].isin(radar_metrics)].copy()
            
            # Normalize values for radar chart
            for metric in radar_metrics:
                min_val = df_radar[df_radar['Metric'] == metric]['Value'].min()
                max_val = df_radar[df_radar['Metric'] == metric]['Value'].max()
                if max_val > min_val:
                    df_radar.loc[df_radar['Metric'] == metric, 'Value'] = (
                        df_radar.loc[df_radar['Metric'] == metric, 'Value'] - min_val
                    ) / (max_val - min_val)
            
            # Create radar chart
            fig = go.Figure()
            
            strategies = df_radar['Strategy'].unique()
            colors = ['blue', 'green', 'red', 'purple']
            
            for i, strategy in enumerate(strategies):
                df_strat = df_radar[df_radar['Strategy'] == strategy]
                fig.add_trace(go.Scatterpolar(
                    r=df_strat['Value'].values,
                    theta=df_strat['Metric'].values,
                    fill='toself',
                    name=strategy,
                    line_color=colors[i]
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )
                ),
                title="Strategy Performance Comparison",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Error displaying strategy performance: {e}")
            st.error(f"An error occurred while displaying strategy performance: {str(e)}")

if __name__ == "__main__":
    # For testing the page individually
    show() 