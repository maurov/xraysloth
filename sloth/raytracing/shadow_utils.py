#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""shadow_utils: simple various utilities for SHADOW3_

.. _SHADOW3: https://github.com/srio/shadow3

"""

import sys, os
import math
import numpy as np

def get_src_hdiv(oe_xhw, oe_ydist):
    """get source horizontal divergence

    :param oe_xhw: optical element X half width
    :param oe_ydist: optical element distance from source
    
    """
    return math.atan(oe_xhw/oe_ydist)

def get_src_vdiv(oe_yhw, oe_ydist, oe_th):
    """get source vertical divergence

    :param oe_yhw: optical element Y half width
    :param oe_ydist: optical element distance from source
    :param oe_th: optical element grazing angle in degrees (e.g. Bragg angle)

    """
    _rth = math.radians(oe_th)
    _h = oe_yhw * math.sin(_rth)
    _d = oe_ydist + oe_yhw * math.cos(_rth)
    return math.atan(_h/_d)


if __name__ == '__main__':
    pass
