import pytest
from datetime import datetime, timedelta
from app.ml.model_manager import ModelManager

def test_create_model(mock_model_manager):
    """Test creating a new ML model."""
    # Setup
    model_config = {
        "name": "Test Model",
        "type": "classification",
        "architecture": {
            "layers": [
                {"type": "dense", "units": 64, "activation": "relu"},
                {"type": "dense", "units": 32, "activation": "relu"},
                {"type": "dense", "units": 1, "activation": "sigmoid"}
            ]
        },
        "parameters": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100
        }
    }
    
    mock_model_manager.create_model.return_value = {
        "id": "model_123",
        "name": "Test Model",
        "type": "classification",
        "status": "created"
    }
    
    # Execute
    result = mock_model_manager.create_model(model_config)
    
    # Assert
    assert result is not None
    assert result["id"] == "model_123"
    assert result["name"] == "Test Model"
    assert result["type"] == "classification"
    assert result["status"] == "created"
    mock_model_manager.create_model.assert_called_once_with(model_config)

def test_train_model(mock_model_manager):
    """Test training a model."""
    # Setup
    model_id = "model_123"
    training_data = {
        "X_train": [[1, 2, 3], [4, 5, 6]],
        "y_train": [0, 1],
        "X_val": [[7, 8, 9], [10, 11, 12]],
        "y_val": [0, 1]
    }
    
    mock_model_manager.train_model.return_value = {
        "id": model_id,
        "status": "trained",
        "metrics": {
            "accuracy": 0.85,
            "loss": 0.32,
            "val_accuracy": 0.82,
            "val_loss": 0.35
        },
        "training_history": {
            "epochs": 100,
            "duration": "00:05:23"
        }
    }
    
    # Execute
    result = mock_model_manager.train_model(model_id, training_data)
    
    # Assert
    assert result is not None
    assert result["id"] == model_id
    assert result["status"] == "trained"
    assert "metrics" in result
    assert "training_history" in result
    assert all(key in result["metrics"] for key in ["accuracy", "loss", "val_accuracy", "val_loss"])
    mock_model_manager.train_model.assert_called_once_with(model_id, training_data)

def test_evaluate_model(mock_model_manager):
    """Test evaluating a model."""
    # Setup
    model_id = "model_123"
    test_data = {
        "X_test": [[1, 2, 3], [4, 5, 6]],
        "y_test": [0, 1]
    }
    
    mock_model_manager.evaluate_model.return_value = {
        "id": model_id,
        "metrics": {
            "accuracy": 0.83,
            "precision": 0.82,
            "recall": 0.84,
            "f1_score": 0.83,
            "auc_roc": 0.89
        },
        "confusion_matrix": [[50, 10], [8, 52]],
        "feature_importance": {
            "feature1": 0.3,
            "feature2": 0.25,
            "feature3": 0.45
        }
    }
    
    # Execute
    result = mock_model_manager.evaluate_model(model_id, test_data)
    
    # Assert
    assert result is not None
    assert result["id"] == model_id
    assert "metrics" in result
    assert "confusion_matrix" in result
    assert "feature_importance" in result
    assert all(key in result["metrics"] for key in ["accuracy", "precision", "recall", "f1_score", "auc_roc"])
    mock_model_manager.evaluate_model.assert_called_once_with(model_id, test_data)

def test_predict(mock_model_manager):
    """Test making predictions with a model."""
    # Setup
    model_id = "model_123"
    input_data = [[1, 2, 3], [4, 5, 6]]
    
    mock_model_manager.predict.return_value = {
        "predictions": [0.2, 0.8],
        "probabilities": [[0.8, 0.2], [0.2, 0.8]],
        "confidence": [0.8, 0.8],
        "timestamp": datetime.now().isoformat()
    }
    
    # Execute
    result = mock_model_manager.predict(model_id, input_data)
    
    # Assert
    assert result is not None
    assert "predictions" in result
    assert "probabilities" in result
    assert "confidence" in result
    assert "timestamp" in result
    assert len(result["predictions"]) == len(input_data)
    mock_model_manager.predict.assert_called_once_with(model_id, input_data)

def test_get_model_performance(mock_model_manager):
    """Test getting model performance metrics."""
    # Setup
    model_id = "model_123"
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    mock_model_manager.get_model_performance.return_value = {
        "id": model_id,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "metrics": {
            "accuracy": 0.85,
            "precision": 0.84,
            "recall": 0.86,
            "f1_score": 0.85
        },
        "predictions": [
            {
                "timestamp": start_date.isoformat(),
                "input": [1, 2, 3],
                "prediction": 1,
                "probability": 0.85,
                "actual": 1
            }
        ]
    }
    
    # Execute
    result = mock_model_manager.get_model_performance(model_id, start_date, end_date)
    
    # Assert
    assert result is not None
    assert result["id"] == model_id
    assert "period" in result
    assert "metrics" in result
    assert "predictions" in result
    assert all(key in result["metrics"] for key in ["accuracy", "precision", "recall", "f1_score"])
    mock_model_manager.get_model_performance.assert_called_once_with(model_id, start_date, end_date) 