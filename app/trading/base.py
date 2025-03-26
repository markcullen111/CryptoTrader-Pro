from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class Order:
    """Order data class."""
    id: str
    symbol: str
    type: str
    side: str
    amount: float
    price: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class Position:
    """Position data class."""
    id: str
    symbol: str
    side: str
    amount: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    created_at: datetime
    updated_at: datetime

class BaseTradingComponent(ABC):
    """Base class for trading components with common functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the trading component.
        
        Args:
            config: Component configuration
        """
        self.config = config
        self.logger = setup_logger(self.__class__.__name__)
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the component.
        
        Returns:
            bool: True if initialization was successful
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources."""
        pass
    
    def validate_config(self) -> bool:
        """Validate component configuration.
        
        Returns:
            bool: True if configuration is valid
        """
        try:
            required_fields = self.get_required_config_fields()
            for field in required_fields:
                if field not in self.config:
                    self.logger.error(f"Missing required config field: {field}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Error validating config: {str(e)}")
            return False
    
    @abstractmethod
    def get_required_config_fields(self) -> List[str]:
        """Get list of required configuration fields.
        
        Returns:
            List[str]: List of required field names
        """
        pass
    
    def log_error(self, message: str, error: Exception) -> None:
        """Log an error with proper formatting.
        
        Args:
            message: Error message
            error: Exception object
        """
        self.logger.error(f"{message}: {str(error)}")
    
    def log_info(self, message: str) -> None:
        """Log an info message.
        
        Args:
            message: Info message
        """
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log a warning message.
        
        Args:
            message: Warning message
        """
        self.logger.warning(message)
    
    def format_error_response(self, message: str, error: Exception) -> Dict[str, Any]:
        """Format an error response.
        
        Args:
            message: Error message
            error: Exception object
            
        Returns:
            Dict[str, Any]: Formatted error response
        """
        return {
            'success': False,
            'message': message,
            'error': str(error)
        }
    
    def format_success_response(self, data: Any = None) -> Dict[str, Any]:
        """Format a success response.
        
        Args:
            data: Response data
            
        Returns:
            Dict[str, Any]: Formatted success response
        """
        return {
            'success': True,
            'data': data
        } 