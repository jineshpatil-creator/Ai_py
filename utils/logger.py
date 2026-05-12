import logging
import os
from datetime import datetime

def setup_logger(name="qa_framework"):
    """Configures and returns an enterprise-grade logger."""
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if logger is already configured
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        
        # Create formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
        )

        # Console Handler (Prints to terminal)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler (Writes to logs/ directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(current_dir, "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"test_execution_{date_str}.log")
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Create a singleton logger instance to be imported across the framework
log = setup_logger()
