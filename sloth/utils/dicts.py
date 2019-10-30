#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dictionaries utilities
=========================

Basic dictionary manipulation
"""
import collections
import six

#: Python 3.8+ compatibility
try:
    collectionsAbc = collections.abc
except Exception:
    collectionsAbc = collections


def update_nested(d, u):
    """Update a nested dictionary

    From: https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in six.iteritems(u):
        dv = d.get(k, {})
        if not isinstance(dv, collectionsAbc.Mapping):
            d[k] = v
        elif isinstance(v, collectionsAbc.Mapping):
            d[k] = update_nested(dv, v)
        else:
            d[k] = v
    return d


if __name__ == "__main__":
    pass