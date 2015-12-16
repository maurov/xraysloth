#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Collection of simple 3D geometry utilities

Sources
=======

The following functions are simply grabbed for the net. In this case,
their own license apply.


.. _src_geom3 : https://github.com/phire/Python-Ray-tracer/blob/master/geom3.py

.. _src_circle_3p : http://stackoverflow.com/questions/20314306/find-arc-circle-equation-given-three-points-in-space-3d

.. _src_point_on_plane_projection : http://stackoverflow.com/questions/7565748/3d-orthogonal-projection-on-a-plane


"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2015"

import os, sys
import math
import numpy as np

epsilon = 1.E-10 # Default epsilon for equality testing of points and vectors

#############################
### dot/cross/length/unit ###
#############################

def dot(v1, v2):
    """Dot product of two vectors"""
    return v1.dot(v2)

def cross(v1, v2):
    """Cross product of two vectors"""
    return v1.cross(v2)

def length(v):
    """Length of vector"""
    return math.sqrt(v.dot(v))

def unit(v):
    """A unit vector in the direction of v"""
    return v / length(v)

########################
### SIMPLE FUNCTIONS ###
########################

def circle_3p(A, B, C):
    """get center and radius of a circle given 3 points in space"""
    a = np.linalg.norm(C - B)
    b = np.linalg.norm(C - A)
    c = np.linalg.norm(B - A)
    s = (a + b + c) / 2
    R = a*b*c / 4 / np.sqrt(s * (s - a) * (s - b) * (s - c))
    b1 = a*a * (b*b + c*c - a*a)
    b2 = b*b * (a*a + c*c - b*b)
    b3 = c*c * (a*a + b*b - c*c)
    P = np.column_stack((A, B, C)).dot(np.hstack((b1, b2, b3)))
    P /= b1 + b2 + b3
    return R, P

def circle_radius(point, center):
    """get circle radius given a point and center as 3D arrays"""
    x, y, z = point[:]
    x0, y0, z0 = center[:]
    return math.sqrt((x-x0)**2 + (y-y0)**2 + (z-z0)**2)

def lines2_intersect(p10, p11, p20, p21):
    """get intesection point, assuming line1 and line2 intersect and
    represented by two points each line, respectively, (p10, p11)
    and (p20, p21)

    """
    t = (p20 - p10) / (p11 - p10 - p21 + p20)
    return p10 + t * (p11 - p10)

def angle_3p(p0, p1, p2):
    """get the angle between three 3D points, p0 is the intersection point"""
    u, v = p1-p0, p2-p0
    costheta = u.dot(v) / math.sqrt(u.dot(u) * v.dot(v))
    return math.degrees(math.acos(costheta))

def point_on_plane_projection(point, plane, test=False):
    """get the orthogonal projection of a 3d point on plane

    Parameters
    ----------
    
    point : 3d P(x,y,z) => np.array([x,y,z])
    
    plane : Ax+By+Cz+d=0, norm = (A,B,C)
            => np.array([norm_x, norm_y, norm_z, d])
    
    Returns
    -------

    proj_pt : projected point = point - norm * offset
              => np.array([proj_x, proj_y, proj_z])
        
    """
    try:
        norm = plane[:-1]
        d = plane[-1]
        offset = (point.dot(norm) + d) / norm.dot(norm)
    except:
        raise NameError('something wrong in point_on_plane_projection')
    proj_pt = point - norm * offset
    if test:
        assert (norm.dot(proj_pt) + d <= epsilon)
    return proj_pt


if __name__ == '__main__':
    pass
