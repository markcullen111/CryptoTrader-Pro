import os
import logging
import logging.handlers
import colorlog
from pathlib import Path
from datetime import datetime
import sys
from logging.handlers import RotatingFileHandler

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """Set up a logger with both file and console handlers.
    
    Args:
        name: The name of the logger
        log_dir: Directory to store log files
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        filename=f"{log_dir}/{name}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def setup_trading_logger(config=None):
    """
    Set up the main trading bot logger based on configuration.
    
    Args:
        config (dict, optional): Configuration dictionary. If None, default values will be used.
        
    Returns:
        logging.Logger: The main trading bot logger
    """
    # Default values
    if config is None:
        config = {}
    
    log_level_str = config.get('general', {}).get('log_level', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Determine log file path
    project_root = Path(__file__).parent.parent.parent
    log_dir = project_root / "data" / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"trading_bot_{timestamp}.log"
    
    # Set up the logger
    return setup_logger(
        name="trading_bot",
        log_dir=str(log_dir)
    )

def log_exception(logger, message=None):
    """
    Log an exception with traceback.
    
    Args:
        logger (logging.Logger): Logger to use
        message (str, optional): Optional message to prepend to the exception
    """
    import traceback
    
    if message:
        logger.error(message)
    
    exc_info = sys.exc_info()
    logger.error("Exception occurred:", exc_info=exc_info)
    
    # Log traceback to file
    if logger.handlers:
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.stream.write(traceback.format_exc())
                handler.stream.flush()

if __name__ == "__main__":
    # Example usage
    logger = setup_trading_logger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    try:
        1 / 0
    except Exception:
        log_exception(logger, "An error occurred while dividing by zero") 