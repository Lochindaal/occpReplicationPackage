import logging
import os

from protocol.utils.config_utils import load_config


def init_logger():
    log_config = load_config()["LOGGING"]
    log_formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    root_logger = logging.getLogger(log_config["LogName"])

    full_log_path = os.path.join(log_config["LogDir"], log_config["LogFile"])
    file_handler = logging.FileHandler(full_log_path)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    return root_logger
