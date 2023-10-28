import time
import logging
from functools import wraps

# Logging setup
logging.basicConfig(level=logging.DEBUG)  # Change to logging.INFO to see less verbose logs
logger = logging.getLogger(__name__)

def retry_on_exception(n_retry, delay_s, debug=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts <= n_retry:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if debug:
                        logger.debug(f"Attempt {attempts} failed with error: {e}")
                    if attempts > n_retry:
                        raise  # If max retries reached, raise the exception
                    time.sleep(delay_s)
        return wrapper
    return decorator

# Example usage:
@retry_on_exception(n_retry=3, delay_s=2, debug=True)  # Set debug=True to see error logs
def some_function():
    print("Trying...")
    raise Exception("Sample error")

some_function()
