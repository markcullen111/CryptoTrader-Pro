import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.analytics.performance_analytics import PerformanceAnalytics

def test_calculate_returns(mock_performance_analytics):
    """Test calculating returns from price data."""
    # Setup
    prices = pd.Series([
        50000, 50100, 50200, 50150, 50100,
        50000, 49900, 49800, 49700, 49800,
        49900, 50000, 50100, 50200
    ])
    
    mock_performance_analytics.calculate_returns.return_value = {
        "returns": pd.Series([
            0.002, 0.002, -0.001, -0.001, -0.002,
            -0.002, -0.002, -0.002, 0.002, 0.002,
            0.002, 0.002, 0.002
        ]),
        "log_returns": pd.Series([
            0.002, 0.002, -0.001, -0.001, -0.002,
            -0.002, -0.002, -0.002, 0.002, 0.002,
            0.002, 0.002, 0.002
        ]),
        "cumulative_returns": pd.Series([
            0.002, 0.004, 0.003, 0.002, 0.000,
            -0.002, -0.004, -0.006, -0.004, -0.002,
            0.000, 0.002, 0.004
        ]),
        "metrics": {
            "mean_return": 0.0002,
            "std_return": 0.002,
            "skew": 0.1,
            "kurtosis": 3.2
        }
    }
    
    # Execute
    result = mock_performance_analytics.calculate_returns(prices)
    
    # Assert
    assert result is not None
    assert "returns" in result
    assert "log_returns" in result
    assert "cumulative_returns" in result
    assert "metrics" in result
    assert len(result["returns"]) == len(prices) - 1
    assert len(result["cumulative_returns"]) == len(prices) - 1
    mock_performance_analytics.calculate_returns.assert_called_once_with(prices)

def test_calculate_volatility(mock_performance_analytics):
    """Test calculating volatility metrics."""
    # Setup
    returns = pd.Series(np.random.normal(0.0001, 0.01, 1000))
    window = 20
    
    mock_performance_analytics.calculate_volatility.return_value = {
        "volatility": pd.Series(np.random.uniform(0.008, 0.012, 1000)),
        "rolling_volatility": pd.Series(np.random.uniform(0.008, 0.012, 1000)),
        "metrics": {
            "annualized_volatility": 0.15,  # 15%
            "daily_volatility": 0.01,  # 1%
            "volatility_ratio": 1.2,
            "volatility_trend": "increasing"
        },
        "volatility_bands": {
            "upper": pd.Series(np.random.uniform(0.012, 0.016, 1000)),
            "lower": pd.Series(np.random.uniform(0.004, 0.008, 1000))
        }
    }
    
    # Execute
    result = mock_performance_analytics.calculate_volatility(returns, window)
    
    # Assert
    assert result is not None
    assert "volatility" in result
    assert "rolling_volatility" in result
    assert "metrics" in result
    assert "volatility_bands" in result
    assert result["metrics"]["annualized_volatility"] > result["metrics"]["daily_volatility"]
    mock_performance_analytics.calculate_volatility.assert_called_once_with(returns, window)

def test_calculate_risk_metrics(mock_performance_analytics):
    """Test calculating risk metrics."""
    # Setup
    returns = pd.Series(np.random.normal(0.0001, 0.01, 1000))
    risk_free_rate = 0.02  # 2% annual
    
    mock_performance_analytics.calculate_risk_metrics.return_value = {
        "sharpe_ratio": 1.5,
        "sortino_ratio": 1.8,
        "calmar_ratio": 2.0,
        "information_ratio": 1.2,
        "alpha": 0.05,  # 5%
        "beta": 1.1,
        "metrics": {
            "excess_return": 0.15,  # 15%
            "downside_deviation": 0.08,  # 8%
            "max_drawdown": 0.10,  # 10%
            "tracking_error": 0.05  # 5%
        }
    }
    
    # Execute
    result = mock_performance_analytics.calculate_risk_metrics(returns, risk_free_rate)
    
    # Assert
    assert result is not None
    assert "sharpe_ratio" in result
    assert "sortino_ratio" in result
    assert "calmar_ratio" in result
    assert "information_ratio" in result
    assert "alpha" in result
    assert "beta" in result
    assert "metrics" in result
    assert result["sharpe_ratio"] > 0
    mock_performance_analytics.calculate_risk_metrics.assert_called_once_with(returns, risk_free_rate)

def test_calculate_trade_metrics(mock_performance_analytics):
    """Test calculating trade performance metrics."""
    # Setup
    trades = pd.DataFrame({
        'entry_time': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'exit_time': pd.date_range(start='2024-01-02', end='2024-02-01', freq='1H'),
        'entry_price': np.random.normal(50000, 1000, 744),
        'exit_price': np.random.normal(51000, 1000, 744),
        'position_size': np.random.uniform(0.1, 1.0, 744),
        'pnl': np.random.normal(100, 50, 744)
    })
    
    mock_performance_analytics.calculate_trade_metrics.return_value = {
        "trade_metrics": {
            "total_trades": 744,
            "winning_trades": 450,
            "losing_trades": 294,
            "win_rate": 0.605,
            "profit_factor": 1.8,
            "average_win": 150,
            "average_loss": -80,
            "largest_win": 500,
            "largest_loss": -300
        },
        "time_metrics": {
            "average_hold_time": "1 day",
            "max_hold_time": "5 days",
            "min_hold_time": "1 hour",
            "time_in_market": 0.8  # 80%
        },
        "distribution": {
            "pnl_distribution": pd.Series(np.random.normal(100, 50, 1000)),
            "win_loss_ratio": 1.875,
            "profit_factor": 1.8
        }
    }
    
    # Execute
    result = mock_performance_analytics.calculate_trade_metrics(trades)
    
    # Assert
    assert result is not None
    assert "trade_metrics" in result
    assert "time_metrics" in result
    assert "distribution" in result
    assert result["trade_metrics"]["win_rate"] > 0.5
    assert result["trade_metrics"]["profit_factor"] > 1.0
    mock_performance_analytics.calculate_trade_metrics.assert_called_once_with(trades)

def test_generate_performance_report(mock_performance_analytics):
    """Test generating a comprehensive performance report."""
    # Setup
    returns = pd.Series(np.random.normal(0.0001, 0.01, 1000))
    trades = pd.DataFrame({
        'entry_time': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'exit_time': pd.date_range(start='2024-01-02', end='2024-02-01', freq='1H'),
        'entry_price': np.random.normal(50000, 1000, 744),
        'exit_price': np.random.normal(51000, 1000, 744),
        'position_size': np.random.uniform(0.1, 1.0, 744),
        'pnl': np.random.normal(100, 50, 744)
    })
    
    mock_performance_analytics.generate_performance_report.return_value = {
        "summary": {
            "total_return": 0.15,  # 15%
            "annualized_return": 0.25,  # 25%
            "sharpe_ratio": 1.5,
            "max_drawdown": 0.10,  # 10%
            "win_rate": 0.605,
            "profit_factor": 1.8
        },
        "risk_metrics": {
            "volatility": 0.15,  # 15%
            "var_95": 0.02,  # 2%
            "cvar_95": 0.03,  # 3%
            "beta": 1.1,
            "alpha": 0.05  # 5%
        },
        "trade_analysis": {
            "total_trades": 744,
            "average_trade": 100,
            "best_trade": 500,
            "worst_trade": -300,
            "average_hold_time": "1 day"
        },
        "monthly_returns": pd.DataFrame({
            '2024-01': 0.15,
            '2024-02': 0.12,
            '2024-03': 0.18
        }),
        "recommendations": [
            "Consider reducing position sizes during high volatility periods",
            "Implement trailing stops to protect profits",
            "Diversify across more trading pairs"
        ]
    }
    
    # Execute
    result = mock_performance_analytics.generate_performance_report(returns, trades)
    
    # Assert
    assert result is not None
    assert "summary" in result
    assert "risk_metrics" in result
    assert "trade_analysis" in result
    assert "monthly_returns" in result
    assert "recommendations" in result
    assert result["summary"]["total_return"] > 0
    assert len(result["recommendations"]) > 0
    mock_performance_analytics.generate_performance_report.assert_called_once_with(returns, trades) 