#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handling loggers
"""
import logging


def setup_logger(logger):
    """Return a logger with a default ColoredFormatter."""
    try:
        from colorlog import ColoredFormatter
    except ModuleNotFoundError:
        return logger
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red',
        }
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def test_logger(logger):
    """Test custom logger"""
    logger = setup_logger(logger)
    logger.debug('a debug message')
    logger.info('an info message')
    logger.warning('a warning message')
    logger.error('an error message')
    logger.critical('a critical message')


def getLogger(name=None, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


if __name__ == '__main__':
    pass
