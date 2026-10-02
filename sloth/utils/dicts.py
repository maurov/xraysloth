#!/usr/bin/env python

"""Dictionaries utilities
=========================

Basic dictionary manipulation
"""
import collections.abc


def update_nested(d, u):
    """Update a nested dictionary

    From: https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in u.items():
        dv = d.get(k, {})
        if not isinstance(dv, collections.abc.Mapping):
            d[k] = v
        elif isinstance(v, collections.abc.Mapping):
            d[k] = update_nested(dv, v)
        else:
            d[k] = v
    return d


if __name__ == "__main__":
    pass