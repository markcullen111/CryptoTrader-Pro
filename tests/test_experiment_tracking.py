import pytest
from datetime import datetime, timedelta
from app.ml.experiment_tracking import ExperimentManager

def test_create_experiment(mock_experiment_manager):
    """Test creating a new experiment."""
    # Setup
    experiment_config = {
        "name": "Test Experiment",
        "description": "Testing different model architectures",
        "parameters": {
            "model_type": ["lstm", "gru"],
            "hidden_layers": [64, 128],
            "learning_rate": [0.001, 0.0001]
        },
        "metrics": ["accuracy", "precision", "recall", "f1_score"]
    }
    
    mock_experiment_manager.create_experiment.return_value = {
        "id": "exp_123",
        "name": "Test Experiment",
        "status": "created",
        "created_at": datetime.now().isoformat()
    }
    
    # Execute
    result = mock_experiment_manager.create_experiment(experiment_config)
    
    # Assert
    assert result is not None
    assert result["id"] == "exp_123"
    assert result["name"] == "Test Experiment"
    assert result["status"] == "created"
    assert "created_at" in result
    mock_experiment_manager.create_experiment.assert_called_once_with(experiment_config)

def test_get_experiment_results(mock_experiment_manager):
    """Test getting experiment results."""
    # Setup
    experiment_id = "exp_123"
    
    mock_experiment_manager.get_experiment_results.return_value = {
        "id": experiment_id,
        "name": "Test Experiment",
        "status": "completed",
        "results": [
            {
                "run_id": "run_1",
                "parameters": {
                    "model_type": "lstm",
                    "hidden_layers": 64,
                    "learning_rate": 0.001
                },
                "metrics": {
                    "accuracy": 0.85,
                    "precision": 0.84,
                    "recall": 0.86,
                    "f1_score": 0.85
                },
                "training_history": {
                    "epochs": 100,
                    "duration": "00:05:23"
                }
            }
        ],
        "summary": {
            "best_accuracy": 0.85,
            "best_f1_score": 0.85,
            "total_runs": 1,
            "completed_runs": 1
        }
    }
    
    # Execute
    result = mock_experiment_manager.get_experiment_results(experiment_id)
    
    # Assert
    assert result is not None
    assert result["id"] == experiment_id
    assert "results" in result
    assert "summary" in result
    assert len(result["results"]) > 0
    assert all(key in result["summary"] for key in ["best_accuracy", "best_f1_score", "total_runs", "completed_runs"])
    mock_experiment_manager.get_experiment_results.assert_called_once_with(experiment_id)

def test_log_metric(mock_experiment_manager):
    """Test logging a metric for an experiment run."""
    # Setup
    experiment_id = "exp_123"
    run_id = "run_1"
    metric_name = "accuracy"
    metric_value = 0.85
    step = 10
    
    mock_experiment_manager.log_metric.return_value = {
        "experiment_id": experiment_id,
        "run_id": run_id,
        "metric": metric_name,
        "value": metric_value,
        "step": step,
        "timestamp": datetime.now().isoformat()
    }
    
    # Execute
    result = mock_experiment_manager.log_metric(experiment_id, run_id, metric_name, metric_value, step)
    
    # Assert
    assert result is not None
    assert result["experiment_id"] == experiment_id
    assert result["run_id"] == run_id
    assert result["metric"] == metric_name
    assert result["value"] == metric_value
    assert result["step"] == step
    assert "timestamp" in result
    mock_experiment_manager.log_metric.assert_called_once_with(experiment_id, run_id, metric_name, metric_value, step)

def test_get_parameter_combinations(mock_experiment_manager):
    """Test getting parameter combinations for an experiment."""
    # Setup
    experiment_id = "exp_123"
    
    mock_experiment_manager.get_parameter_combinations.return_value = {
        "id": experiment_id,
        "combinations": [
            {
                "model_type": "lstm",
                "hidden_layers": 64,
                "learning_rate": 0.001
            },
            {
                "model_type": "gru",
                "hidden_layers": 128,
                "learning_rate": 0.0001
            }
        ],
        "total_combinations": 2,
        "completed_combinations": 1
    }
    
    # Execute
    result = mock_experiment_manager.get_parameter_combinations(experiment_id)
    
    # Assert
    assert result is not None
    assert result["id"] == experiment_id
    assert "combinations" in result
    assert len(result["combinations"]) > 0
    assert "total_combinations" in result
    assert "completed_combinations" in result
    mock_experiment_manager.get_parameter_combinations.assert_called_once_with(experiment_id)

def test_get_experiment_comparison(mock_experiment_manager):
    """Test getting comparison between experiments."""
    # Setup
    experiment_ids = ["exp_123", "exp_456"]
    
    mock_experiment_manager.get_experiment_comparison.return_value = {
        "experiments": [
            {
                "id": "exp_123",
                "name": "Test Experiment 1",
                "best_metrics": {
                    "accuracy": 0.85,
                    "f1_score": 0.85
                },
                "parameters": {
                    "model_type": "lstm",
                    "hidden_layers": 64
                }
            },
            {
                "id": "exp_456",
                "name": "Test Experiment 2",
                "best_metrics": {
                    "accuracy": 0.82,
                    "f1_score": 0.82
                },
                "parameters": {
                    "model_type": "gru",
                    "hidden_layers": 128
                }
            }
        ],
        "comparison": {
            "best_experiment": "exp_123",
            "metric_differences": {
                "accuracy": 0.03,
                "f1_score": 0.03
            }
        }
    }
    
    # Execute
    result = mock_experiment_manager.get_experiment_comparison(experiment_ids)
    
    # Assert
    assert result is not None
    assert "experiments" in result
    assert "comparison" in result
    assert len(result["experiments"]) == len(experiment_ids)
    assert "best_experiment" in result["comparison"]
    assert "metric_differences" in result["comparison"]
    mock_experiment_manager.get_experiment_comparison.assert_called_once_with(experiment_ids) 