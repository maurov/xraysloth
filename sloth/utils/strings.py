"""
###############
### STRINGS ###
###############

:mod:`sloth.utils.strings`
"""
def str2rng(rngstr, keeporder=True, rebin=None):
    """simple utility to convert a generic string representing a compact
    list of scans to a sorted list of integers

    Parameters
    ----------
    rngstr : string with given syntax (see Example below)
    keeporder : boolean [True], to keep the original order
                keeporder=False turn into a sorted list
    rebin : integer [None], force rebinning of the final range

    Example
    -------
    > _str2rng('100, 7:9, 130:140:5, 14, 16:18:1')
    > [7, 8, 9, 14, 16, 17, 18, 100, 130, 135, 140]

    """
    _rng = []
    for _r in rngstr.split(', '): #the space is important!
        if (len(_r.split(',')) > 1):
            raise NameError("Space after comma(s) is missing in '{0}'".format(_r))
        _rsplit2 = _r.split(':')
        if (len(_rsplit2) == 1):
            _rng.append(_r)
        elif (len(_rsplit2) == 2 or len(_rsplit2) == 3):
            if len(_rsplit2) == 2 :
                _rsplit2.append('1')
            if (_rsplit2[0] == _rsplit2[1]):
                raise NameError("Wrong range '{0}' in string '{1}'".format(_r, rngstr))
            if (int(_rsplit2[0]) > int(_rsplit2[1])):
                raise NameError("Wrong range '{0}' in string '{1}'".format(_r, rngstr))
            _rng.extend(range(int(_rsplit2[0]), int(_rsplit2[1])+1, int(_rsplit2[2])))
        else:
            raise NameError("Too many colon in {0}".format(_r))

    #create the list and return it (removing the duplicates)
    _rngout = [int(x) for x in _rng]

    if rebin is not None:
        try:
            _rngout = _rngout[::int(rebin)]
        except:
            raise NameError("Wrong rebin={0}".format(int(rebin)))

    def uniquify(seq):
        # Order preserving uniquifier by Dave Kirby
        seen = set()
        return [x for x in seq if x not in seen and not seen.add(x)]

    if keeporder:
        return uniquify(_rngout)
    else:
        return list(set(_rngout))
