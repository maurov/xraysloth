#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Simple color print """

__author__ = 'Mauro Rovezzi'
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = 'ESRF beamline control unit'
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__version__ = "0.0.1"
__status__ = "Alpha"
__date__ = "November 2013"

# settings
CPRINT_PAR = {}

def cprint_set_light_background():
    CPRINT_PAR["light_background"] = 1
    CPRINT_PAR["dark_background"]  = 0

def cprint_set_dark_background():
    CPRINT_PAR["dark_background"]  = 1
    CPRINT_PAR["light_background"] = 0

def cprint_colors_enabled():
    """ Check if usage of colors with cprint* functions is enabled """
    return (CPRINT_PAR["colors"])

def cprint_enable_colors():
    CPRINT_PAR["colors"] = 1

def cprint_disable_colors():
    CPRINT_PAR["colors"] = 0

### CONTRAST CHECKS ###
def _cprint_bad_contrast(fgcolor, bgcolor, bold, underlined):
    """ Returns 1 if one of the conditions of poor contrast is matched """

    #### ALL BG
    _c0 = (fgcolor == bgcolor)
    _c5 = (fgcolor == 1) and (bgcolor == 5)
    _c6 = (fgcolor == 2) and (bgcolor == 6)

    #### DARK BG
    _c1 = (fgcolor==4) and ((bgcolor==8) or (bgcolor==0))
    _c2 = (fgcolor == 5) and (bgcolor == 1) and (CPRINT_PAR["dark_background"])
    _c3 = (fgcolor == 6) and (bgcolor == 2) and (CPRINT_PAR["dark_background"])
    _c4 = (fgcolor == 8) and (bgcolor == 7) and (CPRINT_PAR["dark_background"])
    _c7 = (fgcolor == 4) and (bgcolor == 6) and (CPRINT_PAR["dark_background"])

    if ( _c0 or _c1 or _c2 or _c3 or _c4 or _c5 or _c6 or _c7):
        return 1
    else:
        return 0

def _cprint_bad_contrast2(fgcolor, bgcolor, bold, underlined):
    """ Returns 1 if one of the conditions of poor contrast is matched """

    #### LIGHT BG
    _c1 = (fgcolor == 3) and (bgcolor == 8) and (bold == 1) and (CPRINT_PAR["light_background"])
    _c2 = (fgcolor == 7) and (bgcolor == 8) and (bold == 1) and (CPRINT_PAR["light_background"])

    if ( _c1 or _c2):
        return 1
    else:
        return 0

def _cprint_bad_contrast3(fgcolor, bgcolor, bold, underlined):
    """ Returns 1 if one of the conditions of poor contrast is matched """

    #### black on black with LIGHT BG
    _c1 = (fgcolor == 8) and (bgcolor == 0) and (CPRINT_PAR["light_background"])

    if ( _c1 ):
        return 1
    else:
        return 0

### COLOR PRINT ###

def bprint(str):
    """ returns a bold <str>"""
    return "\033[1m{0}\033[0m".format (str)

def cprint_bold(str):
    """ Prints <str> in bold """
    print bprint(str)

def buprint(str):
    """ returns underlined bold <str>"""
    return "\033[1m\033[4m{0}\033[0m".format(str)

def cprint_bold_underlined(str):
    """ prints underlined bold <str>"""
    print buprint(str)

def uprint(str):
    """ returns underlined <str> """
    return "\033[4m{0}\033[0m".format(str)

def cprint_underlined(str):
    """ prints underlined <str> """
    print uprint(str)

def cprint(_str, fgcolor, bgcolor, bold, underlined, st):
    """
    Prints <str> with color and attributes.
    <fgcolor>    : foreground color : 0..8   (0=black 8=current fg color)
    <bgcolor>    : background color : 0..8   (0=black 8=current bg color)
    <bold>       : +bold
    <underlined> : +underlined
    <st>         : +Strikethrough
    """

    _bad_contrast  = _cprint_bad_contrast(fgcolor, bgcolor, bold, underlined)
    _bad_contrast2 = _cprint_bad_contrast2(fgcolor, bgcolor, bold, underlined)
    _bad_contrast3 = _cprint_bad_contrast3(fgcolor, bgcolor, bold, underlined)

    # Bold
    _b_str  = "\033[1m"
    # Underlined
    _u_str  = "\033[4m"
    # Striked-trougth
    _st_str = "\033[9m"

    # Formating the color strings.
    if (_bad_contrast3):
        # replace (current fg color black) on black by white on black.
        _fg_str = "\033[3{0}m".format(7)
    else:
        _fg_str = "\033[3{0}m".format(fgcolor)

    if (bgcolor >= 0):
        _bg_str = "\033[4{0}m".format(bgcolor)
    else:
        _bg_str = ""

    if ( CPRINT_PAR["colors"] == 0 ):
        _fg_str = ""
        _bg_str = ""

    # Formating the modificator strings.
    _mod_str = ""

    if ((bold or _bad_contrast) and (_bad_contrast2 == 0)):
        _mod_str = _mod_str + _b_str

    if (underlined):
        _mod_str = _mod_str + _u_str

    if (st):
        _mod_str = _mod_str + _st_str

    _colored_str = "{0}{1}{2}{3}\033[0m\n".format(_mod_str, _fg_str, _bg_str, _str)

    print _colored_str

def cprint_examples():
    """ prints 'Ab1' string in many colored and modified typos """

    mystr = "Ab1 "

    print "        color print"
    print "usage : cprint(str, <p1>, <p2>, <p3>, <p4>)"
    print ""
    print "p1\\p2-> 0               1               2               3           "      \
        "    4               5               6               7               8     "

    for ii in range(9):
        print "{0}--".format(ii)
        for jj in range(9):
            cprint("{0}{1}".format(mystr,ii), ii , jj, 0, 0, 0)
            cprint("{0}{1}".format(mystr,ii), ii , jj, 1, 0, 0)
            cprint("{0}{1}".format(mystr,ii), ii , jj, 0, 1, 0)
            cprint("{0}{1}".format(mystr,ii), ii , jj, 1, 1, 0)

if __name__ == '__main__':
    cprint_enable_colors()
    cprint_set_light_background()
