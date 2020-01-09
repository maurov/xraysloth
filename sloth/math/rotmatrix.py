#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rotation matrix using the `Euler-Rodrigues formula
<http://en.wikipedia.org/wiki/Euler%E2%80%93Rodrigues_parameters>`_

Rotation using the `right hand rule
<http://en.wikipedia.org/wiki/Right_hand_rule>`_

Code downloaded from
`<http://stackoverflow.com/questions/6802577/python-rotation-of-3d-vector>`_
"""

import numpy as np
import math


def rotation_matrix_numpy(axis, theta):
    """ return the rotation matrix using numpy

    Parameters
    ----------
    axis : numpy.array([x,y,z])
    theta : rotation angle in radians
    """
    mat = np.eye(3, 3)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)

    return np.array(
        [
            [a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
            [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
            [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - b * b - c * c],
        ]
    )


def rotation_matrix_weave(axis, theta, mat=None):
    """ return the rotation matrix using Weave
    (~20x faster than numpy)

    Parameters
    ----------
    axis : numpy.array([x,y,z])
    theta : rotation angle in radians
    """
    if mat == None:
        mat = np.eye(3, 3)

    support = "#include <math.h>"
    code = """
    double x = sqrt(axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2]);
    double a = cos(theta / 2.0);
    double b = -(axis[0] / x) * sin(theta / 2.0);
    double c = -(axis[1] / x) * sin(theta / 2.0);
    double d = -(axis[2] / x) * sin(theta / 2.0);

    mat[0] = a*a + b*b - c*c - d*d;
    mat[1] = 2 * (b*c - a*d);
    mat[2] = 2 * (b*d + a*c);

    mat[3*1 + 0] = 2*(b*c+a*d);
    mat[3*1 + 1] = a*a+c*c-b*b-d*d;
    mat[3*1 + 2] = 2*(c*d-a*b);

    mat[3*2 + 0] = 2*(b*d-a*c);
    mat[3*2 + 1] = 2*(c*d+a*b);
    mat[3*2 + 2] = a*a+d*d-b*b-c*c;
    """

    weave.inline(code, ["axis", "theta", "mat"], support_code=support, libraries=["m"])

    return mat


def rotate(arr, axis, theta, method="numpy"):
    """ rotate array around axis by theta with 'numpy' or 'weave'

    Arguments
    ---------
    arr : np.array([x,y,z])
    axis : np.array([x,y,z])
    theta : in radians
    method : 'numpy' or 'weave'

    Returns
    -------
    np.array([x,y,z])

    """
    if method == "numpy":
        return np.dot(rotation_matrix_numpy(axis, theta), arr)
    elif method == "weave":
        return np.dot(rotation_matrix_weave(axis, theta), arr)
    else:
        raise NameError("method for rotation matrix is 'numpy' or 'weave'")


if __name__ == "__main__":
    v = np.array([3, 5, 0])
    axis = np.array([4, 4, 1])
    theta = 1.2

    print("Rotation with Numpy:")
    print(np.dot(rotation_matrix_numpy(axis, theta), v))
    print("Rotation with Scipy.Weave:")
    print(np.dot(rotation_matrix_weave(axis, theta), v))
