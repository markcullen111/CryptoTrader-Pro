import pytest
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture
def test_data_dir():
    """Fixture to provide the path to test data directory."""
    return Path(__file__).parent / "data"

@pytest.fixture
def mock_exchange_client(mocker):
    """Fixture to provide a mocked exchange client."""
    from app.trading.exchange_client import ExchangeClient
    mock_client = mocker.Mock(spec=ExchangeClient)
    return mock_client

@pytest.fixture
def mock_strategy_manager(mocker):
    """Fixture to provide a mocked strategy manager."""
    from app.trading.strategy_manager import StrategyManager
    mock_manager = mocker.Mock(spec=StrategyManager)
    return mock_manager

@pytest.fixture
def mock_model_manager(mocker):
    """Fixture to provide a mocked model manager."""
    from app.ml.model_manager import ModelManager
    mock_manager = mocker.Mock(spec=ModelManager)
    return mock_manager

@pytest.fixture
def sample_market_data():
    """Fixture to provide sample market data."""
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H')
    data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.normal(100, 10, len(dates)),
        'high': np.random.normal(105, 10, len(dates)),
        'low': np.random.normal(95, 10, len(dates)),
        'close': np.random.normal(100, 10, len(dates)),
        'volume': np.random.normal(1000, 100, len(dates))
    })
    return data

@pytest.fixture
def sample_trade_data():
    """Fixture to provide sample trade data."""
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H')
    data = pd.DataFrame({
        'timestamp': dates,
        'symbol': ['BTC/USDT'] * len(dates),
        'side': np.random.choice(['buy', 'sell'], len(dates)),
        'price': np.random.normal(50000, 1000, len(dates)),
        'amount': np.random.normal(0.1, 0.01, len(dates)),
        'cost': np.random.normal(5000, 100, len(dates))
    })
    return data

@pytest.fixture
def sample_model_data():
    """Fixture to provide sample model data."""
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H')
    data = pd.DataFrame({
        'timestamp': dates,
        'prediction': np.random.choice([0, 1], len(dates)),
        'probability': np.random.random(len(dates)),
        'actual': np.random.choice([0, 1], len(dates))
    })
    return data 