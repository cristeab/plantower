import logging
import logging.handlers


class LoggerConfigurator:
    log_level = logging.INFO

    def __init__(self):
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # File handler with rotation (5 files x 10MB)
        self.file_handler = logging.handlers.RotatingFileHandler(
            'aqi_system.log',
            maxBytes=10*1024*1024,
            backupCount=5
        )
        self.file_handler.setFormatter(formatter)

    @staticmethod
    def configure_logger(class_name):
        logger = logging.getLogger(f"AQI.{class_name}")

        lc = LoggerConfigurator()
        logger.setLevel(lc.log_level)
        logger.addHandler(lc.file_handler)
        return logger
    
    @staticmethod
    def set_handler(logger):
        # Remove any existing handlers to avoid duplication
        logger.handlers.clear()

        lc = LoggerConfigurator()
        logger.setLevel(lc.log_level)
        logger.addHandler(lc.file_handler)
