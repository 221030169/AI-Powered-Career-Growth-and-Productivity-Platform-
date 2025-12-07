import logging
import os
import time
from functools import wraps
# --- Logger Setup ---
LOG_FILE_NAME = "performance.log" # Name of the log file
LOG_DIR = "logs" # Directory for logs
# Ensure log directory exists
log_file_path = os.path.join(LOG_DIR, LOG_FILE_NAME)
os.makedirs(LOG_DIR, exist_ok=True)
# Configure the logger
# Set up a logger specifically for performance timing
performance_logger = logging.getLogger('performance_logger')
performance_logger.setLevel(logging.INFO) # Log INFO level messages and above
# Create a file handler which logs even debug messages
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the handler to the logger
performance_logger.addHandler(file_handler)

# Optional: Add a console handler for real-time feedback in terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
# performance_logger.addHandler(console_handler) # Uncomment if you want live logging in terminal too

# --- Timing Decorator ---
def time_function(func):
    """
    A decorator that logs the execution time of the decorated function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        
        # Log the function's execution time
        performance_logger.info(f"Function '{func.__name__}' took {duration:.4f} seconds to execute.")
        
        return result
    return wrapper

if __name__ == "__main__":
    # Example usage:
    @time_function
    def example_task(seconds):
        time.sleep(seconds)
        return f"Slept for {seconds} seconds"

    performance_logger.info("Logger setup complete. Running example task.")
    example_task(0.5)
    example_task(1.2)
    performance_logger.info(f"Check '{log_file_path}' for logs.")
