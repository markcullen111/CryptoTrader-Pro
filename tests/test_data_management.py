import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.data.data_manager import DataManager

def test_fetch_market_data(mock_data_manager):
    """Test fetching market data from the exchange."""
    # Setup
    symbol = "BTC/USDT"
    timeframe = "1h"
    start_time = datetime.now() - timedelta(days=30)
    end_time = datetime.now()
    
    mock_data_manager.fetch_market_data.return_value = {
        "data": pd.DataFrame({
            'timestamp': pd.date_range(start=start_time, end=end_time, freq='1H'),
            'open': np.random.normal(50000, 1000, 720),
            'high': np.random.normal(50500, 1000, 720),
            'low': np.random.normal(49500, 1000, 720),
            'close': np.random.normal(50000, 1000, 720),
            'volume': np.random.normal(100, 10, 720)
        }),
        "metadata": {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "rows": 720,
            "missing_values": 0
        }
    }
    
    # Execute
    result = mock_data_manager.fetch_market_data(symbol, timeframe, start_time, end_time)
    
    # Assert
    assert result is not None
    assert "data" in result
    assert "metadata" in result
    assert isinstance(result["data"], pd.DataFrame)
    assert len(result["data"]) == 720
    assert result["metadata"]["symbol"] == symbol
    mock_data_manager.fetch_market_data.assert_called_once_with(symbol, timeframe, start_time, end_time)

def test_save_market_data(mock_data_manager):
    """Test saving market data to storage."""
    # Setup
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'open': np.random.normal(50000, 1000, 744),
        'high': np.random.normal(50500, 1000, 744),
        'low': np.random.normal(49500, 1000, 744),
        'close': np.random.normal(50000, 1000, 744),
        'volume': np.random.normal(100, 10, 744)
    })
    
    metadata = {
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "source": "exchange",
        "last_updated": datetime.now().isoformat()
    }
    
    mock_data_manager.save_market_data.return_value = {
        "status": "success",
        "file_path": "data/market_data/BTC_USDT_1h_20240101_20240131.csv",
        "rows_saved": 744,
        "metadata": metadata
    }
    
    # Execute
    result = mock_data_manager.save_market_data(data, metadata)
    
    # Assert
    assert result is not None
    assert result["status"] == "success"
    assert "file_path" in result
    assert result["rows_saved"] == 744
    assert result["metadata"] == metadata
    mock_data_manager.save_market_data.assert_called_once_with(data, metadata)

def test_load_market_data(mock_data_manager):
    """Test loading market data from storage."""
    # Setup
    file_path = "data/market_data/BTC_USDT_1h_20240101_20240131.csv"
    
    mock_data_manager.load_market_data.return_value = {
        "data": pd.DataFrame({
            'timestamp': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
            'open': np.random.normal(50000, 1000, 744),
            'high': np.random.normal(50500, 1000, 744),
            'low': np.random.normal(49500, 1000, 744),
            'close': np.random.normal(50000, 1000, 744),
            'volume': np.random.normal(100, 10, 744)
        }),
        "metadata": {
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "source": "local",
            "last_updated": datetime.now().isoformat()
        }
    }
    
    # Execute
    result = mock_data_manager.load_market_data(file_path)
    
    # Assert
    assert result is not None
    assert "data" in result
    assert "metadata" in result
    assert isinstance(result["data"], pd.DataFrame)
    assert len(result["data"]) == 744
    assert result["metadata"]["source"] == "local"
    mock_data_manager.load_market_data.assert_called_once_with(file_path)

def test_update_market_data(mock_data_manager):
    """Test updating market data with new data."""
    # Setup
    existing_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', end='2024-01-30', freq='1H'),
        'open': np.random.normal(50000, 1000, 720),
        'high': np.random.normal(50500, 1000, 720),
        'low': np.random.normal(49500, 1000, 720),
        'close': np.random.normal(50000, 1000, 720),
        'volume': np.random.normal(100, 10, 720)
    })
    
    new_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-31', end='2024-01-31', freq='1H'),
        'open': np.random.normal(50000, 1000, 24),
        'high': np.random.normal(50500, 1000, 24),
        'low': np.random.normal(49500, 1000, 24),
        'close': np.random.normal(50000, 1000, 24),
        'volume': np.random.normal(100, 10, 24)
    })
    
    mock_data_manager.update_market_data.return_value = {
        "status": "success",
        "updated_data": pd.concat([existing_data, new_data]),
        "rows_added": 24,
        "rows_updated": 0,
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_rows": 744
        }
    }
    
    # Execute
    result = mock_data_manager.update_market_data(existing_data, new_data)
    
    # Assert
    assert result is not None
    assert result["status"] == "success"
    assert "updated_data" in result
    assert result["rows_added"] == 24
    assert result["metadata"]["total_rows"] == 744
    mock_data_manager.update_market_data.assert_called_once_with(existing_data, new_data)

def test_validate_market_data(mock_data_manager):
    """Test validating market data."""
    # Setup
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'open': np.random.normal(50000, 1000, 744),
        'high': np.random.normal(50500, 1000, 744),
        'low': np.random.normal(49500, 1000, 744),
        'close': np.random.normal(50000, 1000, 744),
        'volume': np.random.normal(100, 10, 744)
    })
    
    validation_config = {
        "check_missing": True,
        "check_duplicates": True,
        "check_outliers": True,
        "check_consistency": True
    }
    
    mock_data_manager.validate_market_data.return_value = {
        "is_valid": True,
        "validation_results": {
            "missing_values": 0,
            "duplicates": 0,
            "outliers": 0,
            "inconsistent_rows": 0
        },
        "data_quality": {
            "completeness": 1.0,
            "consistency": 1.0,
            "accuracy": 1.0
        }
    }
    
    # Execute
    result = mock_data_manager.validate_market_data(data, validation_config)
    
    # Assert
    assert result is not None
    assert result["is_valid"] is True
    assert "validation_results" in result
    assert "data_quality" in result
    assert all(value == 0 for value in result["validation_results"].values())
    assert all(value == 1.0 for value in result["data_quality"].values())
    mock_data_manager.validate_market_data.assert_called_once_with(data, validation_config) 