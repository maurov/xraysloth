#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Full Sloth test suite"""
import logging
import os
import unittest

logger = logging.getLogger(__name__)

def suite():
    from . import test_version

    test_suite = unittest.TestSuite()
    test_suite.addTest(test_version.suite())

    return test_suite


def run_tests():
    """Run test complete test_suite"""
    runner = unittest.TextTestRunner()
    if not runner.run(suite()).wasSuccessful():
        print("Test suite failed")
    else:
        print("Test suite succeeded")
