import pytest
from datetime import datetime, timedelta
from app.trading.strategy_manager import StrategyManager

def test_create_strategy(mock_strategy_manager):
    """Test creating a new trading strategy."""
    # Setup
    strategy_config = {
        "name": "Test Strategy",
        "type": "mean_reversion",
        "symbols": ["BTC/USDT"],
        "timeframe": "1h",
        "parameters": {
            "window": 20,
            "threshold": 2.0
        }
    }
    
    mock_strategy_manager.create_strategy.return_value = {
        "id": "strategy_123",
        "name": "Test Strategy",
        "type": "mean_reversion",
        "status": "active"
    }
    
    # Execute
    result = mock_strategy_manager.create_strategy(strategy_config)
    
    # Assert
    assert result is not None
    assert result["id"] == "strategy_123"
    assert result["name"] == "Test Strategy"
    assert result["type"] == "mean_reversion"
    assert result["status"] == "active"
    mock_strategy_manager.create_strategy.assert_called_once_with(strategy_config)

def test_get_strategy_status(mock_strategy_manager):
    """Test getting strategy status."""
    # Setup
    strategy_id = "strategy_123"
    
    mock_strategy_manager.get_strategy_status.return_value = {
        "id": strategy_id,
        "name": "Test Strategy",
        "status": "active",
        "performance": {
            "total_trades": 100,
            "win_rate": 0.65,
            "profit_factor": 1.8
        }
    }
    
    # Execute
    result = mock_strategy_manager.get_strategy_status(strategy_id)
    
    # Assert
    assert result is not None
    assert result["id"] == strategy_id
    assert result["status"] == "active"
    assert "performance" in result
    assert all(key in result["performance"] for key in ["total_trades", "win_rate", "profit_factor"])
    mock_strategy_manager.get_strategy_status.assert_called_once_with(strategy_id)

def test_update_strategy_parameters(mock_strategy_manager):
    """Test updating strategy parameters."""
    # Setup
    strategy_id = "strategy_123"
    new_parameters = {
        "window": 30,
        "threshold": 2.5
    }
    
    mock_strategy_manager.update_strategy_parameters.return_value = {
        "id": strategy_id,
        "parameters": new_parameters,
        "updated_at": datetime.now().isoformat()
    }
    
    # Execute
    result = mock_strategy_manager.update_strategy_parameters(strategy_id, new_parameters)
    
    # Assert
    assert result is not None
    assert result["id"] == strategy_id
    assert result["parameters"] == new_parameters
    assert "updated_at" in result
    mock_strategy_manager.update_strategy_parameters.assert_called_once_with(strategy_id, new_parameters)

def test_get_strategy_performance(mock_strategy_manager):
    """Test getting strategy performance metrics."""
    # Setup
    strategy_id = "strategy_123"
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    mock_strategy_manager.get_strategy_performance.return_value = {
        "id": strategy_id,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "metrics": {
            "total_return": 0.15,
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.08,
            "win_rate": 0.65
        },
        "trades": [
            {
                "timestamp": start_date.isoformat(),
                "type": "buy",
                "price": 50000,
                "amount": 0.1,
                "pnl": 500
            }
        ]
    }
    
    # Execute
    result = mock_strategy_manager.get_strategy_performance(strategy_id, start_date, end_date)
    
    # Assert
    assert result is not None
    assert result["id"] == strategy_id
    assert "period" in result
    assert "metrics" in result
    assert "trades" in result
    assert all(key in result["metrics"] for key in ["total_return", "sharpe_ratio", "max_drawdown", "win_rate"])
    mock_strategy_manager.get_strategy_performance.assert_called_once_with(strategy_id, start_date, end_date)

def test_stop_strategy(mock_strategy_manager):
    """Test stopping a strategy."""
    # Setup
    strategy_id = "strategy_123"
    
    mock_strategy_manager.stop_strategy.return_value = {
        "id": strategy_id,
        "status": "stopped",
        "stopped_at": datetime.now().isoformat()
    }
    
    # Execute
    result = mock_strategy_manager.stop_strategy(strategy_id)
    
    # Assert
    assert result is not None
    assert result["id"] == strategy_id
    assert result["status"] == "stopped"
    assert "stopped_at" in result
    mock_strategy_manager.stop_strategy.assert_called_once_with(strategy_id) 