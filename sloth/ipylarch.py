#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An IPython shell for Larch

Author
======
Mauro Rovezzi <mauro.rovezzi@gmail.com>

Credits
=======
- http://ipython.org/ipython-doc/dev/interactive/reference.html#embedding-ipython
- https://github.com/xraypy/xraylarch
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = "IPython community, Matt Newville"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__version__ = "0.0.1"
__status__ = "Alpha"
__date__ = "July 2013"

### IMPORTS ###
from IPython.config.loader import Config
from IPython.frontend.terminal.embed import InteractiveShellEmbed

# first check if there is already an IPython shell running
try:
    get_ipython
except NameError:
    nested = 0
    cfg = Config()
    prompt_config = cfg.PromptManager
    prompt_config.in_template = 'In [\\#]: '
    prompt_config.in2_template = '   .\\D.: '
    prompt_config.out_template = 'Out[\\#]: '
else:
    print("Running nested copies of IPython.")
    print("The prompts for the nested copy have been modified")
    cfg = Config()
    nested = 1

# Now create an instance of the embeddable shell. The first argument is a
# string with options exactly as you would type them if you were starting
# IPython at the system command line. Any parameters you want to define for
# configuration can thus be specified here.

banner = """IPyLarch: custom IPython environment for Larch"""
outmsg = "Leaving IPyLarch, have a nice day!"
ipshell = InteractiveShellEmbed(config=cfg,
                                banner1=banner,
                                exit_msg=outmsg)

### SYSTEM AND USEFUL IMPORTS ###
import os, sys
import numpy as np

### TEST LARCH ###
from larch import use_plugin_path, Interpreter, Group
use_plugin_path('std')
use_plugin_path('io')
use_plugin_path('wx')
use_plugin_path('math')
use_plugin_path('xafs')
# now we can reliably import other Larch modules...
from columnfile import _read_ascii as read_ascii
from specfile import str2rng, spec_getmap2group
from plotter import _plot as plot
from xafsft import xftf, xftr, xftf_prep, xftf_fast, xftr_fast, ftwindow 

# additional plugins
from larch.site_config import plugins_path
try:
    sys.path.append(plugins_path[0])
    from gsutils import gslist
except:
    pass

mylarch = Interpreter()

# can we, and should we, use wx?
HAS_WX = False
if not hasattr(sys, 'frozen'):
    try:
        import wxversion
        wxversion.ensureMinimal('2.8')
    except:
        pass
    try:
        import wx
        HAS_WX = True
    except ImportError:
        HAS_WX = False

def onCtrlC(*args, **kws):
    return 0

# use inputhook to enable wx
if HAS_WX:
    from larch.wxlib import inputhook
    app = wx.App(redirect=False, clearSigInt=False)
    # print 'has group _sys.wx? ', shell.larch.symtable.has_group('_sys.wx')
    mylarch.symtable.set_symbol('_sys.wx.inputhook', inputhook)
    mylarch.symtable.set_symbol('_sys.wx.ping',   inputhook.ping)
    mylarch.symtable.set_symbol('_sys.wx.force_wxupdate', False)
    mylarch.symtable.set_symbol('_sys.wx.wxapp', app)
    mylarch.symtable.set_symbol('_sys.wx.parent',None)
    inputhook.ON_INTERRUPT = onCtrlC
    inputhook.WXLARCH_SYM = mylarch.symtable

if __name__ == '__main__':
    ipshell()
