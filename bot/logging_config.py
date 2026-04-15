"""
logging_config.py
-----------------
Sets up logging so that:
  - INFO and above goes to the console (so you can see what's happening live)
  - DEBUG and above goes to a log file called trading_bot.log (full details saved)

Usage: call setup_logging() once at the start of your program.
"""

import logging


def setup_logging(log_file: str = "trading_bot.log") -> logging.Logger:
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # File Handler: saves EVERYTHING (DEBUG+) to a log file
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)

    # Console Handler: shows INFO+ messages in the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_format)

    # Avoid duplicate handlers if called more than once
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger