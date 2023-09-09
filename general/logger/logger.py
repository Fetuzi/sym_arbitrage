import logging
import os
import threading
from datetime import datetime


class CustomLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pid = os.getpid()
        self.tid = threading.get_ident()


logging.setLogRecordFactory(CustomLogRecord)


log_format = '[%(asctime)s.%(msecs)03d][%(pid)s][%(tid)s][%(levelname)s][%(filename)s:%(lineno)d]%(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(log_format, date_format)


def setup_logger(name=__name__, log_file=None, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(level)
    logger.addHandler(stream_handler)
    return logger
