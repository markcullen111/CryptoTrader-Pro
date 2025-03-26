import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class TradingConfig:
    """Trading configuration data class."""
    trading_pairs: list[str]
    default_timeframe: str
    max_positions: int
    position_size: float
    stop_loss: float
    take_profit: float

@dataclass
class RiskConfig:
    """Risk management configuration data class."""
    max_drawdown: float
    daily_loss_limit: float
    max_leverage: float
    position_sizing_method: str

@dataclass
class MLConfig:
    """Machine learning configuration data class."""
    model_path: str
    data_path: str
    training_interval: str
    prediction_threshold: float

class ConfigManager:
    """Manages application configuration with validation."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found at {self.config_path}")
                self._create_default_config()
                return
            
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            self._validate_config()
            logger.info("Configuration loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration."""
        self.config = {
            'trading': {
                'trading_pairs': ['BTC/USDT', 'ETH/USDT'],
                'default_timeframe': '1h',
                'max_positions': 3,
                'position_size': 0.1,
                'stop_loss': 0.02,
                'take_profit': 0.05
            },
            'risk': {
                'max_drawdown': 0.1,
                'daily_loss_limit': 0.05,
                'max_leverage': 1.0,
                'position_sizing_method': 'fixed'
            },
            'ml': {
                'model_path': 'models',
                'data_path': 'data',
                'training_interval': '1d',
                'prediction_threshold': 0.7
            }
        }
        self._save_config()
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        required_sections = ['trading', 'risk', 'ml']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate trading config
        trading = self.config['trading']
        if not isinstance(trading['trading_pairs'], list):
            raise ValueError("trading_pairs must be a list")
        if not isinstance(trading['position_size'], (int, float)):
            raise ValueError("position_size must be a number")
        
        # Validate risk config
        risk = self.config['risk']
        if not 0 <= risk['max_drawdown'] <= 1:
            raise ValueError("max_drawdown must be between 0 and 1")
        if not 0 <= risk['daily_loss_limit'] <= 1:
            raise ValueError("daily_loss_limit must be between 0 and 1")
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    def get_trading_config(self) -> TradingConfig:
        """Get trading configuration.
        
        Returns:
            TradingConfig: Trading configuration object
        """
        return TradingConfig(**self.config['trading'])
    
    def get_risk_config(self) -> RiskConfig:
        """Get risk management configuration.
        
        Returns:
            RiskConfig: Risk configuration object
        """
        return RiskConfig(**self.config['risk'])
    
    def get_ml_config(self) -> MLConfig:
        """Get machine learning configuration.
        
        Returns:
            MLConfig: ML configuration object
        """
        return MLConfig(**self.config['ml'])
    
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """Update a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: New value
            
        Returns:
            bool: True if update was successful
        """
        try:
            if section not in self.config:
                raise ValueError(f"Invalid section: {section}")
            
            self.config[section][key] = value
            self._validate_config()
            self._save_config()
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            return False 