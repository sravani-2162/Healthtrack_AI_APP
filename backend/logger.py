import logging
import os
import sys

def setup_logger(log_file="healthtrack_app.log", level=logging.INFO):
    """
    Configures standard logging for HealthTrack application.
    Logs to both a local file and console stdout.
    """
    logger = logging.getLogger("HealthTrack")
    logger.setLevel(level)

    # Avoid duplicate handlers if setup is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Failed to create file logger: {e}\n")

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Module-level default logger
logger = setup_logger()
