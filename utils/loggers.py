import logging
import os
from datetime import datetime

class SimulatorLogger:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SimulatorLogger, cls).__new__(cls, *args, **kwargs)
            cls._instance.init_logger()
        return cls._instance

    def init_logger(self, log_level=logging.INFO):
        self.logger = logging.getLogger("simulator_logger")
        self.logger.setLevel(log_level)

        # Check if logs directory exists, if not, create it
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Format the current timestamp and use it as the filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"simulator_log_{timestamp}.log"
        log_path = os.path.join("logs", log_filename)

        # Create a custom formatter that includes filename and line number
        formatter = logging.Formatter('%(asctime)s - %(name)-20s - %(levelname)-8s - [%(filename)s:%(lineno)d] - %(message)s')
        
        # File handler to write logs to a file inside logs directory
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        
        # Stream handler to write logs to the console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

# initialize the simulator logger
sim_logger_instance = SimulatorLogger().logger