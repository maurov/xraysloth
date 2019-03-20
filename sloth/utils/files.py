"""
#############
### FILES ###
#############

:mod:`sloth.utils.files`
"""
import os
import glob, subprocess

def cp_replace(grepfns, grepstr, rplstr, splitstr='_'):
    """given a filenames search string, copy the files with replaced string

    Parameters
    ----------
    grepfns : string
              search string passed to glob to generate files list to
              copy
    grepstr : string
              string to replace
    rplstr : string
             new string
    splitstr : string, '_'
               string used as separator
    """
    fns = glob.glob(grepfns)
    for fn in fns:
        _fn2 = [w.replace(grepstr, rplstr) for w in fn.split(splitstr)]
        fn2 = splitstr.join(_fn2)
        subprocess.call('cp {0} {1}'.format(fn, fn2), shell=True)
        print(fn2)

def get_fnames(grepstr, rpath=os.getcwd(), substr1=None):
    """get a list of filenames

    Arguments
    ---------
    grepstr : pattern according to the rules used by the Unix shell

    Keyword arguments
    -----------------
    rpath : [os.getcwd()] root path
    substr1 : [None] if given, search first level of subdirs

    """
    if substr1 is not None:
        return glob.glob(os.path.join(rpath, substr1, grepstr))
    else:
        return glob.glob(os.path.join(rpath, grepstr))
