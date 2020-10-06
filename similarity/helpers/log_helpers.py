import logging
import os
import sys
from datetime import datetime
from typing import List

from os.path import basename

CRITICAL = logging.CRITICAL
FATAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

_LOGGERS = {}

logs_dir = 'logs'

LOG_CONFIGS = {
    'file_path': os.path.join(logs_dir, '%s.log' % str(datetime.utcnow().date())),
    'level': INFO
}

LOG_FILES = set()
LOG_FILE_INSTANCES = set()
LOG_FORMAT = '%(asctime)s - %(processName)s[%(process)d] - %(name)s - %(levelname)s ' \
             '- %(message)s (%(filename)s:%(lineno)s)'


def get_logger(name, log_file=True, log_configs=LOG_CONFIGS):
    global _LOGGERS
    formatter = logging.Formatter(LOG_FORMAT)
    if name in _LOGGERS:
        logger = _LOGGERS[name]
    else:
        logger = logging.getLogger(name)
        logger.setLevel(log_configs['level'])
        # add stream handle
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    # add file logger handle if exist file path
    if log_file:
        LOG_FILES.add(log_configs['file_path'])

    for log_file_path in LOG_FILES:
        add_file_handler(logger, log_file_path)

    _LOGGERS[name] = logger
    return logger


def register_new_log_file(log_file_path):
    if log_file_path in LOG_FILES:
        return
    LOG_FILES.add(log_file_path)
    for logger in _LOGGERS.values():
        add_file_handler(logger, log_file_path)


def is_registered_log_file(log_file_path):
    return log_file_path in LOG_FILES


def deregister_log_file(log_file_path):
    if log_file_path not in LOG_FILES:
        return

    LOG_FILES.remove(log_file_path)
    for logger in _LOGGERS.values():
        handlers: List[logging.Handler] = logger.handlers
        filtered_handlers = []
        for h in handlers:
            if isinstance(h, logging.FileHandler):
                if basename(h.baseFilename) == basename(log_file_path):
                    continue

            filtered_handlers.append(h)

        logger.handlers = filtered_handlers


def add_file_handler(logger, log_file_path):
    key = logger.name + '_' + log_file_path
    if key in LOG_FILE_INSTANCES:
        return
    LOG_FILE_INSTANCES.add(key)
    formatter = logging.Formatter(LOG_FORMAT)
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
