#!/usr/bin/env python
"""
Handling exceptions
"""
import numpy as np
import logging
_logger = logging.getLogger('sloth.utils.exceptions')


def checkZeroDivision(numerator, denumerator):
    """Custom ZeroDivisionError handling"""
    try:
        return numerator/denumerator
    except ZeroDivisionError:
        _logger.error("Division by zero!!! -> returning numpy.inf")
        return np.inf
