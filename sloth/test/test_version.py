#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test version"""

import unittest
import sloth

class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertTrue(isinstance(sloth.__version__, str))

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestVersion))
    return test_suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
