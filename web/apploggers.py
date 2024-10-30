import logging
import os
import sys

APP_LOGGER_NAME = 'TennisScoreboardAppLogger'

APP_LOGGER_NAME_FOR_REMOTE_HOST = 'TennisScoreboardRemoteAppLogger'

def make_filter(level):

    def log_filter(logrec: logging.LogRecord):
        return True if logrec.levelno <= getattr(logging, level) else False

    return log_filter

def get_log_dir_name():
    return os.path.join(os.path.split(os.path.dirname(__file__))[0], 'logs')

def make_log_file_dir():
    log_dir = get_log_dir_name()

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)


logconfig = {
    'version': 1,
    'loggers': {
        APP_LOGGER_NAME: {
            'level': 'INFO',
            'handlers': ['to_stderr', 'to_stdout']
        },
        APP_LOGGER_NAME_FOR_REMOTE_HOST: {
            'level': 'INFO',
            'handlers': ['to_file']
        },

    },
    'handlers': {
        'to_stderr': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'plain_logs',
            'stream': 'ext://sys.stderr'
        },
        'to_stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose_debug_logs',
            'filters': ['info_and_below'],
            'stream': 'ext://sys.stdout'
        },
        'to_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose_logs',
            'filename': os.path.join(get_log_dir_name(), 'currexch.log'),
            'maxBytes': 2**20,
            'backupCount': 1
        }
    },
    'filters': {
        'info_and_below': {
            '()': f'{__name__}.make_filter',
            'level': 'INFO'
        },
    },
    'formatters': {
        'plain_logs': {
            'format': '<<<%(levelname)s>>> [%(asctime)s] \n%(message)s\n'
        },
        'verbose_debug_logs': {
            'format': '<<<%(levelname)s>>> [%(asctime)s] %(name)s:%(module)s line-%(lineno)s callable-%(funcName)s \n%(message)s\n'
        }
    }
}
