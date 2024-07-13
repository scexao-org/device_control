from logging.config import dictConfig
from pathlib import Path

LOGDIR = Path("~/logs").expanduser()
LOGDIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file": {
            "format": "%(asctime)s|%(thread)d|%(name)s|%(funcName)s|%(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
        }
    },
    "handlers": {
        "file_position": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOGDIR / "devices_status.log",
            "when": "midnight",
            "utc": True,
            "formatter": "file",
        },
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOGDIR / "devices_debug.log",
            "when": "midnight",
            "utc": True,
            "formatter": "file",
        },
    },
    "loggers": {
        "": {"handlers": ["file_position", "file_debug"], "level": "DEBUG", "propagate": True}
    },
}

dictConfig(LOGGING_CONFIG)
