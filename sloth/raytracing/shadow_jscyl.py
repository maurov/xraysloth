#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Shadow ray-tracing of a Johansson cylindrical analyzer
=========================================================

"""
import math
from sloth.utils.logging import getLogger
from sloth.utils.bragg import bragg_ev
from sloth.raytracing.shadow_utils import get_src_hdiv, get_src_vdiv, rotate_rays

_LOGGER = getLogger("shadow_jscyl", level="DEBUG")

HAS_SHADOW = False
try:
    import Shadow

    Shadow.ShadowTools.plt.ion()
    HAS_SHADOW = True
except ImportError:
    _LOGGER.warning("Shadow not found!")
    pass


#########
# JSCYL #
#########


def jscyl(
    d=None,
    refl_file=None,
    theta0=75.0,
    R=1000.0,
    nrays=50000,
    aw=25.0,
    ah=80.0,
    ene0=None,
    ene0_hw=5.0,
    src_ovf=0.001,
    src_shape="rectangle",
    src_x=0.2,
    src_z=0.1,
    src_rot=False,
    move=None,
    run=True,
    **kwargs
):
    """raytrace a Johansson cylindrical analyzer at a given theta angle

    Notes
    -----
    - units given in mm
    - this works/tested *only* for a symmetric vertical Rowland circle geometry

    Parameters
    ----------
    d : float
        Crystal d-spacing in Ang [None]
    refl_file : string
        Reflectivity file as calculated by Xcrystal (or Bragg) [None]
    theta0 : float
        Incidence angle in deg (= Bragg angle) [75.]
    nrays : int
        Number of rays [50000]
    aw : float
        Dimension of the flat side (=short side) in mm [25.]
    ah : float
        Dimension of the curved side (=long side) in mm [80.]
    R : float
        Bending radius (= diameter Rowland circle) in mm [1000.]
    ene0 : float
        Source central energy in eV [None]
        if None, it is calculated from Bragg angle and d-spacing
    ene0_hw : float
        Source energy half bandwidth in eV [5]
    src_shape : str ['rectangle']
        Spatial source type/shape in X-Z plane. Avaiable
        options are: 'point', 'rectangle' and 'ellipse'
    src_ovf : float
        add extra divergence to overfill the optical element [0.001]
    src_x, src_z : floats
        (WXSOU, WZSOU) -> X,Z size of elliptical source [0.2, 0.1]
    src_rot : boolean
        Rotate the source [False]
    move : None or list of floats
        optical element movement [None]
        [OFFX, OFFY, OFFZ, X_ROT, Y_ROT, Z_ROT]
        where:
            OFF*: X/Y/Z offset mm
            *_ROT: X/Y/Z rotation CCW, deg
    run : boolean
        run Shadow [True]

    Returns
    -------
    (beam, src, oe) : tuple of :class:`Shadow.Beam`, :class:`Shadow.Source`, :class:`Shadow.OE`

    """
    # CHECKS
    if HAS_SHADOW is False:
        _LOGGER.error("Shadow not found!!!")
        return (None, None, None)
    if d is None:
        raise NameError("d-spacing not given!")
    if refl_file is None:
        raise NameError("refl_file not given!")
    #
    iwrite = 0  # write start/end/begin/star files (0=No, 1=Yes) [0]
    p = R * math.sin(math.radians(theta0))  # SYMMETRIC RC GEOMETRY
    # set src energy
    if ene0 is None:
        ene0 = bragg_ev(d, theta0)
    ph1 = ene0 - ene0_hw
    ph2 = ene0 + ene0_hw
    # set src divergence
    hdiv = get_src_hdiv(aw / 2, p) + 1.5 * src_ovf
    vdiv = get_src_vdiv(ah / 2.0, p, theta0) + 3.5 * src_ovf
    # initialize shadow3 source (src) and beam
    beam = Shadow.Beam()
    src = Shadow.Source()
    oe = Shadow.OE()
    # Define source variables. See meaning of variables in:
    #  https://raw.githubusercontent.com/srio/shadow3/master/docs/source.nml
    src.ISTAR1 = 0  # seed 0=system clock
    src.NPOINT = nrays
    #
    src.FDISTR = 2  # uniform
    src.HDIV1 = hdiv
    src.HDIV2 = hdiv
    src.VDIV1 = vdiv
    src.VDIV2 = vdiv
    #
    # src.FDISTR = 5 #conical
    # src.CONE_MAX = 2*hdiv
    #
    if src_shape == "point":
        src.FSOUR = 0
    elif src_shape == "rectangle":
        src.FSOUR = 1
    elif src_shape == "ellipse":
        src.FSOUR = 2
    else:
        raise NameError('src_shape "{0}" not understood!'.format(src_shape))
    #
    src.WXSOU = src_x
    src.WZSOU = src_z
    #
    src.F_COLOR = 3  # 3=uniform energy distribution
    src.F_PHOT = 0  # set eV units
    src.PH1 = ph1
    src.PH2 = ph2
    #
    src.IDO_VX = 0
    src.IDO_VZ = 0
    src.IDO_X_S = 0
    src.IDO_Y_S = 0
    src.IDO_Z_S = 0
    # Define analyzer variables. See meaning of variables in:
    #  https://raw.githubusercontent.com/srio/shadow3/master/docs/oe.nml
    oe.DUMMY = 0.1  # mm
    oe.FCYL = 1
    oe.FHIT_C = 1
    oe.FILE_REFL = bytes(refl_file, "utf8")
    oe.FMIRR = 1
    oe.FWRITE = 1
    oe.F_CRYSTAL = 1
    oe.F_EXT = 1
    oe.F_JOHANSSON = 1
    oe.RLEN1 = ah / 2.0
    oe.RLEN2 = ah / 2.0
    oe.RMIRR = R / 2.0
    oe.RWIDX1 = aw / 2.0
    oe.RWIDX2 = aw / 2.0
    oe.R_JOHANSSON = R
    oe.T_IMAGE = p
    oe.T_INCIDENCE = 90.0 - theta0
    oe.T_REFLECTION = 90.0 - theta0
    oe.T_SOURCE = p
    if move is not None:
        oe.F_MOVE = 1
        oe.OFFX = move[0]
        oe.OFFY = move[1]
        oe.OFFZ = move[2]
        oe.X_ROT = move[3]
        oe.Y_ROT = move[4]
        oe.Z_ROT = move[5]
        if not src_rot:
            # adjust src divergence -> EMPIRICAL ADJUSTMENTS!!!
            hdiv1 = get_src_hdiv(1.05 * move[0] + aw / 2, p) + 7 * src_ovf
            hdiv2 = -1 * (get_src_hdiv(1.05 * move[0] - aw / 2, p) - 5 * src_ovf)
            vdiv1 = get_src_vdiv(2.5 * move[2] + ah / 2.0, p, theta0) + 5 * src_ovf
            vdiv2 = get_src_vdiv(0.5 * move[2] + ah / 2.0, p, theta0) + src_ovf
            src.HDIV1 = hdiv1
            src.HDIV2 = hdiv2
            src.VDIV1 = vdiv1
            src.VDIV2 = vdiv2
            # src.CONE_MAX = hdiv1
            # rotate source -> NOT WORKING!!!
        oe.FSTAT = 0
    if run:
        # Run SHADOW to create the source
        if iwrite:
            src.write("start.00")
        beam.genSource(src)
        if (move is not None) and src_rot:
            rays = beam.rays.copy()
            # rays_ry = rotate_rays(rays, move[4], 2)
            _rz = math.atan(move[0] / p)
            rz = math.degrees(_rz) * 0.5  # empirical factor to reduce!!!
            rays_rz = rotate_rays(rays, rz, 3)
            p1 = p / math.cos(_rz)
            _rx = math.atan(move[5] / p1)
            rx = -1 * math.degrees(_rx) * 0.9  # empirical factor to reduce!!!
            rays_rzrx = rotate_rays(rays_rz, rx, 1)
            beam.rays = rays_rzrx
        if iwrite:
            src.write("end.00")
            beam.write("begin.dat")
        # Run optical element 1
        # _LOGGER.info("running optical element: %d"%(1))
        if iwrite:
            oe.write("start.01")
        beam.traceOE(oe, 1)
        if iwrite:
            oe.write("end.01")
            beam.write("star.01")
    _LOGGER.info("JsCBCA => R={0:.0f} mm, theta0={1:.3f}".format(R, theta0))
    _LOGGER.info("JsCBCA => p[q]={0:.4f} mm , ene0={1:.3f} eV".format(p, ene0))
    return (beam, src, oe)


if __name__ == "__main__":
    pass
