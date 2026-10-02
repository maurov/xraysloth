#!/usr/bin/env python

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


def rotate(arr, axis, theta, method="numpy"):
    """ rotate array around axis by theta

    Arguments
    ---------
    arr : np.array([x,y,z])
    axis : np.array([x,y,z])
    theta : in radians
    method : 'numpy' (only available method)

    Returns
    -------
    np.array([x,y,z])

    """
    if method == "numpy":
        return np.dot(rotation_matrix_numpy(axis, theta), arr)
    else:
        raise NameError("method for rotation matrix is 'numpy'")


if __name__ == "__main__":
    v = np.array([3, 5, 0])
    axis = np.array([4, 4, 1])
    theta = 1.2

    print("Rotation with Numpy:")
    print(np.dot(rotation_matrix_numpy(axis, theta), v))
