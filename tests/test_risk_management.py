import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.trading.risk_manager import RiskManager

def test_calculate_position_size(mock_risk_manager):
    """Test calculating position size based on risk parameters."""
    # Setup
    account_balance = 100000
    risk_per_trade = 0.02  # 2% risk per trade
    entry_price = 50000
    stop_loss = 49000
    
    mock_risk_manager.calculate_position_size.return_value = {
        "position_size": 0.2,  # BTC
        "position_value": 10000,
        "risk_amount": 2000,
        "risk_percentage": 0.02,
        "stop_loss_distance": 1000,
        "leverage": 1.0
    }
    
    # Execute
    result = mock_risk_manager.calculate_position_size(
        account_balance=account_balance,
        risk_per_trade=risk_per_trade,
        entry_price=entry_price,
        stop_loss=stop_loss
    )
    
    # Assert
    assert result is not None
    assert "position_size" in result
    assert "position_value" in result
    assert "risk_amount" in result
    assert result["risk_percentage"] == risk_per_trade
    assert result["position_value"] == result["position_size"] * entry_price
    mock_risk_manager.calculate_position_size.assert_called_once_with(
        account_balance, risk_per_trade, entry_price, stop_loss
    )

def test_check_risk_limits(mock_risk_manager):
    """Test checking if a trade meets risk limits."""
    # Setup
    trade_params = {
        "symbol": "BTC/USDT",
        "position_size": 0.2,
        "entry_price": 50000,
        "stop_loss": 49000,
        "take_profit": 52000,
        "leverage": 1.0
    }
    
    risk_limits = {
        "max_position_size": 1.0,  # BTC
        "max_position_value": 50000,  # USDT
        "max_leverage": 2.0,
        "min_stop_loss_distance": 100,  # USDT
        "min_take_profit_distance": 200,  # USDT
        "max_daily_loss": 0.05  # 5% of account
    }
    
    mock_risk_manager.check_risk_limits.return_value = {
        "is_valid": True,
        "checks": {
            "position_size": True,
            "position_value": True,
            "leverage": True,
            "stop_loss": True,
            "take_profit": True,
            "daily_loss": True
        },
        "warnings": [],
        "errors": []
    }
    
    # Execute
    result = mock_risk_manager.check_risk_limits(trade_params, risk_limits)
    
    # Assert
    assert result is not None
    assert result["is_valid"] is True
    assert "checks" in result
    assert "warnings" in result
    assert "errors" in result
    assert all(result["checks"].values())
    assert len(result["warnings"]) == 0
    assert len(result["errors"]) == 0
    mock_risk_manager.check_risk_limits.assert_called_once_with(trade_params, risk_limits)

def test_calculate_drawdown(mock_risk_manager):
    """Test calculating drawdown metrics."""
    # Setup
    equity_curve = pd.Series([
        100000, 101000, 102000, 101500, 101000,
        100000, 99000, 98000, 97000, 98000,
        99000, 100000, 101000, 102000
    ])
    
    mock_risk_manager.calculate_drawdown.return_value = {
        "max_drawdown": 0.03,  # 3%
        "drawdown_duration": 5,  # periods
        "drawdown_curve": pd.Series([
            0.0, 0.0, 0.0, 0.005, 0.01,
            0.02, 0.025, 0.03, 0.03, 0.02,
            0.01, 0.0, 0.0, 0.0
        ]),
        "drawdown_periods": [
            {"start": 5, "end": 9, "depth": 0.03}
        ]
    }
    
    # Execute
    result = mock_risk_manager.calculate_drawdown(equity_curve)
    
    # Assert
    assert result is not None
    assert "max_drawdown" in result
    assert "drawdown_duration" in result
    assert "drawdown_curve" in result
    assert "drawdown_periods" in result
    assert result["max_drawdown"] == 0.03
    assert result["drawdown_duration"] == 5
    assert len(result["drawdown_periods"]) == 1
    mock_risk_manager.calculate_drawdown.assert_called_once_with(equity_curve)

def test_calculate_var(mock_risk_manager):
    """Test calculating Value at Risk."""
    # Setup
    returns = pd.Series(np.random.normal(0, 0.01, 1000))
    confidence_level = 0.95
    time_horizon = 1  # days
    
    mock_risk_manager.calculate_var.return_value = {
        "var": 0.016,  # 1.6%
        "cvar": 0.022,  # 2.2%
        "confidence_level": confidence_level,
        "time_horizon": time_horizon,
        "distribution": {
            "mean": 0.0,
            "std": 0.01,
            "skew": 0.1,
            "kurtosis": 3.2
        }
    }
    
    # Execute
    result = mock_risk_manager.calculate_var(returns, confidence_level, time_horizon)
    
    # Assert
    assert result is not None
    assert "var" in result
    assert "cvar" in result
    assert "confidence_level" in result
    assert "time_horizon" in result
    assert "distribution" in result
    assert result["var"] < result["cvar"]  # CVaR should be greater than VaR
    mock_risk_manager.calculate_var.assert_called_once_with(returns, confidence_level, time_horizon)

def test_calculate_sharpe_ratio(mock_risk_manager):
    """Test calculating Sharpe ratio."""
    # Setup
    returns = pd.Series(np.random.normal(0.0001, 0.01, 1000))
    risk_free_rate = 0.02  # 2% annual
    trading_days = 252
    
    mock_risk_manager.calculate_sharpe_ratio.return_value = {
        "sharpe_ratio": 1.5,
        "annualized_return": 0.15,  # 15%
        "annualized_volatility": 0.10,  # 10%
        "risk_free_rate": risk_free_rate,
        "trading_days": trading_days,
        "metrics": {
            "daily_return": 0.0001,
            "daily_volatility": 0.01,
            "excess_return": 0.0001 - (risk_free_rate / trading_days)
        }
    }
    
    # Execute
    result = mock_risk_manager.calculate_sharpe_ratio(returns, risk_free_rate, trading_days)
    
    # Assert
    assert result is not None
    assert "sharpe_ratio" in result
    assert "annualized_return" in result
    assert "annualized_volatility" in result
    assert "metrics" in result
    assert result["sharpe_ratio"] > 0  # Positive Sharpe ratio indicates good risk-adjusted returns
    mock_risk_manager.calculate_sharpe_ratio.assert_called_once_with(returns, risk_free_rate, trading_days) 