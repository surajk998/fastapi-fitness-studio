from logging.config import dictConfig


def configure_logging():
    dictConfig(
        config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": " %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "console",
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "ERROR",
                    "formatter": "file",
                    "filename": "fitness_studio.log",
                    "maxBytes": 1024 * 1024,  # 1MB
                    "backupCount": 5,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "fitness_studio": {
                    "handlers": ["rotating_file"],
                    "level": "ERROR",
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "ERROR",
                },
                "databases": {
                    "handlers": ["rotating_file"],
                    "level": "ERROR",
                },
                "aiosqlite": {
                    "handlers": ["rotating_file"],
                    "level": "ERROR",
                },
            },
        }
    )
