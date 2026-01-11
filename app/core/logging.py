import logging
import sys
from pythonjsonlogger import jsonlogger
from app.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['environment'] = settings.environment
        log_record['app_name'] = settings.app_name


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))
    
    if settings.environment == "production":
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            rename_fields={'timestamp': 'timestamp'}
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    root_logger.info(
        f"Logging configured for {settings.app_name} "
        f"in {settings.environment} environment with level {settings.log_level}"
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)