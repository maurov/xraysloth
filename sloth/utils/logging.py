#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handling loggers
"""
import sys
import logging
import tempfile

# set up basic logging configureation to temporary file
_default_format = '%(asctime)s [%(name)-s] %(levelname)-s : %(message)s'
# needs colorlog, not enabled yet!
_default_colors = {'DEBUG': 'cyan',
                   'INFO': 'green',
                   'WARNING': 'yellow',
                   'ERROR':    'red',
                   'CRITICAL': 'red'}

logging.basicConfig(level=logging.DEBUG,
                    format=_default_format,
                    datefmt='%m-%d %H:%M',
                    filename='{0}.log'.format(tempfile.mktemp()),
                    filemode='w')


def getLogger(name, level=logging.INFO):
    """Utility function to get the logger with customization

    Parameters
    ----------
    name : str
        name of the logger
    level : int (optional)
        logging level [logging.INFO]
    profile : str (optional)
        specific profile [None]
        - None
            stream=sys.stderr
        - 'notebook'
            stream=sys.stdout
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    """stderr handler (needed to show log in Jupyter notebook)"""

    formatter = logging.Formatter('[%(name)-s] %(levelname)-s : %(message)s')
    handler.setFormatter(formatter)
    """Create formatter and add it to the handler"""

    # Set STDERR handler as the only handler
    logger.handlers = [handler]

    return logger


def test_logger():
    """Test custom logger"""
    logger = getLogger('test', level=logging.DEBUG)
    logger.debug('a debug message')
    logger.info('an info message')
    logger.warning('a warning message')
    logger.error('an error message')
    logger.critical('a critical message')


if __name__ == '__main__':
    test_logger()
