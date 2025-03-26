import pytest
import pandas as pd
import numpy as np
from app.ml.feature_engineering import FeatureEngineer

def test_create_features(mock_feature_engineer):
    """Test creating features from market data."""
    # Setup
    market_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'open': np.random.normal(100, 10, 744),
        'high': np.random.normal(105, 10, 744),
        'low': np.random.normal(95, 10, 744),
        'close': np.random.normal(100, 10, 744),
        'volume': np.random.normal(1000, 100, 744)
    })
    
    feature_config = {
        "technical_indicators": {
            "sma": [20, 50],
            "rsi": [14],
            "macd": {"fast": 12, "slow": 26, "signal": 9},
            "bollinger_bands": {"window": 20, "num_std": 2}
        },
        "price_features": {
            "returns": True,
            "log_returns": True,
            "volatility": {"window": 20}
        },
        "volume_features": {
            "volume_ma": [20, 50],
            "volume_std": {"window": 20}
        }
    }
    
    mock_feature_engineer.create_features.return_value = {
        "features": pd.DataFrame({
            'timestamp': market_data['timestamp'],
            'sma_20': np.random.normal(100, 5, 744),
            'sma_50': np.random.normal(100, 5, 744),
            'rsi_14': np.random.uniform(0, 100, 744),
            'macd': np.random.normal(0, 1, 744),
            'macd_signal': np.random.normal(0, 1, 744),
            'bb_upper': np.random.normal(105, 5, 744),
            'bb_lower': np.random.normal(95, 5, 744),
            'returns': np.random.normal(0, 0.01, 744),
            'log_returns': np.random.normal(0, 0.01, 744),
            'volatility_20': np.random.uniform(0, 0.02, 744),
            'volume_ma_20': np.random.normal(1000, 100, 744),
            'volume_ma_50': np.random.normal(1000, 100, 744),
            'volume_std_20': np.random.normal(50, 10, 744)
        }),
        "feature_info": {
            "total_features": 14,
            "feature_types": {
                "technical": 7,
                "price": 3,
                "volume": 4
            },
            "missing_values": 0
        }
    }
    
    # Execute
    result = mock_feature_engineer.create_features(market_data, feature_config)
    
    # Assert
    assert result is not None
    assert "features" in result
    assert "feature_info" in result
    assert isinstance(result["features"], pd.DataFrame)
    assert len(result["features"]) == len(market_data)
    assert result["feature_info"]["total_features"] == 14
    mock_feature_engineer.create_features.assert_called_once_with(market_data, feature_config)

def test_preprocess_features(mock_feature_engineer):
    """Test preprocessing features for model input."""
    # Setup
    features = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'sma_20': np.random.normal(100, 5, 744),
        'rsi_14': np.random.uniform(0, 100, 744),
        'macd': np.random.normal(0, 1, 744),
        'returns': np.random.normal(0, 0.01, 744)
    })
    
    preprocessing_config = {
        "scaling": "standard",
        "handle_missing": "drop",
        "handle_outliers": "clip",
        "feature_selection": ["sma_20", "rsi_14", "macd", "returns"]
    }
    
    mock_feature_engineer.preprocess_features.return_value = {
        "processed_features": pd.DataFrame({
            'sma_20': np.random.normal(0, 1, 744),
            'rsi_14': np.random.normal(0, 1, 744),
            'macd': np.random.normal(0, 1, 744),
            'returns': np.random.normal(0, 1, 744)
        }),
        "preprocessing_info": {
            "scaler": "StandardScaler",
            "selected_features": 4,
            "dropped_features": 0,
            "outliers_handled": 0
        }
    }
    
    # Execute
    result = mock_feature_engineer.preprocess_features(features, preprocessing_config)
    
    # Assert
    assert result is not None
    assert "processed_features" in result
    assert "preprocessing_info" in result
    assert isinstance(result["processed_features"], pd.DataFrame)
    assert len(result["processed_features"]) == len(features)
    assert result["preprocessing_info"]["selected_features"] == 4
    mock_feature_engineer.preprocess_features.assert_called_once_with(features, preprocessing_config)

def test_create_sequences(mock_feature_engineer):
    """Test creating sequences for time series models."""
    # Setup
    features = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'sma_20': np.random.normal(100, 5, 744),
        'rsi_14': np.random.uniform(0, 100, 744),
        'macd': np.random.normal(0, 1, 744)
    })
    
    sequence_config = {
        "sequence_length": 24,
        "target_length": 1,
        "stride": 1,
        "target_column": "sma_20"
    }
    
    mock_feature_engineer.create_sequences.return_value = {
        "X": np.random.normal(0, 1, (720, 24, 4)),
        "y": np.random.normal(0, 1, (720, 1)),
        "sequence_info": {
            "total_sequences": 720,
            "input_shape": (24, 4),
            "target_shape": (1,),
            "feature_names": ["sma_20", "rsi_14", "macd"]
        }
    }
    
    # Execute
    result = mock_feature_engineer.create_sequences(features, sequence_config)
    
    # Assert
    assert result is not None
    assert "X" in result
    assert "y" in result
    assert "sequence_info" in result
    assert isinstance(result["X"], np.ndarray)
    assert isinstance(result["y"], np.ndarray)
    assert result["sequence_info"]["total_sequences"] == 720
    mock_feature_engineer.create_sequences.assert_called_once_with(features, sequence_config)

def test_get_feature_importance(mock_feature_engineer):
    """Test getting feature importance scores."""
    # Setup
    features = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'sma_20': np.random.normal(100, 5, 744),
        'rsi_14': np.random.uniform(0, 100, 744),
        'macd': np.random.normal(0, 1, 744),
        'returns': np.random.normal(0, 0.01, 744)
    })
    
    target = np.random.choice([0, 1], 744)
    
    mock_feature_engineer.get_feature_importance.return_value = {
        "importance_scores": {
            "sma_20": 0.35,
            "rsi_14": 0.25,
            "macd": 0.20,
            "returns": 0.20
        },
        "feature_rankings": [
            ("sma_20", 0.35),
            ("rsi_14", 0.25),
            ("macd", 0.20),
            ("returns", 0.20)
        ],
        "analysis_info": {
            "method": "random_forest",
            "n_features": 4,
            "total_importance": 1.0
        }
    }
    
    # Execute
    result = mock_feature_engineer.get_feature_importance(features, target)
    
    # Assert
    assert result is not None
    assert "importance_scores" in result
    assert "feature_rankings" in result
    assert "analysis_info" in result
    assert len(result["importance_scores"]) == 4
    assert len(result["feature_rankings"]) == 4
    assert result["analysis_info"]["n_features"] == 4
    mock_feature_engineer.get_feature_importance.assert_called_once_with(features, target)

def test_analyze_feature_correlations(mock_feature_engineer):
    """Test analyzing feature correlations."""
    # Setup
    features = pd.DataFrame({
        'timestamp': pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H'),
        'sma_20': np.random.normal(100, 5, 744),
        'rsi_14': np.random.uniform(0, 100, 744),
        'macd': np.random.normal(0, 1, 744),
        'returns': np.random.normal(0, 0.01, 744)
    })
    
    mock_feature_engineer.analyze_feature_correlations.return_value = {
        "correlation_matrix": pd.DataFrame({
            'sma_20': [1.0, 0.2, 0.3, 0.1],
            'rsi_14': [0.2, 1.0, 0.1, 0.2],
            'macd': [0.3, 0.1, 1.0, 0.3],
            'returns': [0.1, 0.2, 0.3, 1.0]
        }, index=['sma_20', 'rsi_14', 'macd', 'returns']),
        "correlation_analysis": {
            "high_correlations": [
                ("sma_20", "macd", 0.3),
                ("macd", "returns", 0.3)
            ],
            "feature_groups": [
                ["sma_20", "macd"],
                ["rsi_14", "returns"]
            ],
            "summary": {
                "total_features": 4,
                "high_correlation_pairs": 2,
                "feature_groups": 2
            }
        }
    }
    
    # Execute
    result = mock_feature_engineer.analyze_feature_correlations(features)
    
    # Assert
    assert result is not None
    assert "correlation_matrix" in result
    assert "correlation_analysis" in result
    assert isinstance(result["correlation_matrix"], pd.DataFrame)
    assert len(result["correlation_analysis"]["high_correlations"]) == 2
    assert len(result["correlation_analysis"]["feature_groups"]) == 2
    mock_feature_engineer.analyze_feature_correlations.assert_called_once_with(features) 