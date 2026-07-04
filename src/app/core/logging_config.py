import logging.config
import os

from .config import get_config


config = get_config()

os.makedirs(config.logs_path, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "core_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": config.logs_path + "/core.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf8",
        },
        "web_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": config.logs_path + "/web.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "app.core": {
            "handlers": ["console", "core_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "app.web": {
            "handlers": ["console", "web_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

def init_logging():
    logging.config.dictConfig(LOGGING_CONFIG)