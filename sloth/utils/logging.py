#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Handling loggers
"""
import sys
import logging
# import tempfile

# set up default logging configureation
_default_format = '[%(name)-s] %(levelname)-s : %(message)s'
_default_format_file = '%(asctime)s [%(name)-s] %(levelname)-s : %(message)s'
_default_datefmt = '%Y-%m-%d %H:%M'
_levels = {'DEBUG': logging.DEBUG,
           'INFO': logging.INFO,
           'WARNING': logging.WARNING,
           'ERROR': logging.ERROR,
           'FATAL': logging.FATAL,
           'CRITICAL': logging.CRITICAL}

# # needs colorlog, not enabled yet!
# _default_colors = {'DEBUG': 'cyan',
#                    'INFO': 'green',
#                    'WARNING': 'yellow',
#                    'ERROR':    'red',
#                    'CRITICAL': 'red'}
#


def enable_basicConfig(level='INFO'):
    """logging basic configuration"""
    logging.basicConfig(level=_levels[level],
                        format=_default_format,
                        datefmt=_default_datefmt)
                        # filename='{0}.log'.format(tempfile.mktemp()),
                        # filemode='w')


def getLogger(name, level='INFO'):
    """Utility function to get the logger with customization

    .. warning:: NOT WORKING AS EXPECTED -> FIXME!!!

    Parameters
    ----------
    name : str
        name of the logger
    level : str (optional)
        logging level ['INFO']
    profile : str (optional)
        specific profile [None]
        - None
            stream=sys.stderr
        - 'notebook'
            stream=sys.stdout
    """
    enable_basicConfig(level=level)
    logger = logging.getLogger(name)
    logger.setLevel(_levels[level])
    return logger

    # handler = logging.StreamHandler(sys.stderr)
    # """stderr handler (needed to show log in Jupyter notebook)"""

    # formatter = logging.Formatter(_default_format)
    # handler.setFormatter(formatter)
    # """Create formatter and add it to the handler"""

    # if (logger.hasHandlers()):
    #     logger.handlers.clear()
    # logger.addHandler(handler)
    # """Clear existing handlers and add current one"""

    # return logger


def test_logger(level='DEBUG'):
    """Test custom logger"""
    logger = getLogger('test', level=level)
    logger.debug('a debug message')
    logger.info('an info message')
    logger.warning('a warning message')
    logger.error('an error message')
    logger.critical('a critical message')


if __name__ == '__main__':
    test_logger()
