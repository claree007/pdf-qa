import logging.handlers
import sys
import logging
from cfg import Cfg

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

def init_logger():
    # print to console
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
            '%(levelname)s %(asctime)s line:%(lineno)d %(message)s'))
    root_logger.addHandler(handler)

    # print to file
    handler = logging.FileHandler(Cfg.logging_file_path)
    handler.setFormatter(logging.Formatter(
            '%(levelname)s %(asctime)s line:%(lineno)d %(message)s'))
    root_logger.addHandler(handler)
    logging.info("Logger initialized")