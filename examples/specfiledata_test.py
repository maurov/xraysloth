#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests/Examples for SpecfileData and SpecfileDataWriter

TODO
====
- spefiledatawriter examples
"""

__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2013-2014"
__version__ = "0.9.6"
__status__ = "Beta"
__date__ = "Aug 2014"

from specfiledata import SpecfileData

### TESTS ###
def test01():
    """ test get_scan method """
    fname = os.path.join(_curDir, 'specfiledata_test.dat')
    signal = 'zap_det_dtc'
    monitor = 'arr_I02sum'
    seconds = 'arr_seconds'
    counter = 'arr_hdh_ene'
    motor = 'Spec.Energy'
    motor_counter = 'arr_xes_en'
    scan = 3
    t = SpecfileData(fname)
    for norm in [None, "area", "max", "max-min", "sum"]:
        x, y, motors, infos = t.get_scan(scan, cntx=counter, csig=signal, cmon=monitor, csec=seconds, norm=norm)
        print("Read scan {0} with normalization {1}".format(scan, norm))
        import matplotlib.pyplot as plt
        plt.ion()
        plt.figure(num=test01.__doc__)
        plt.plot(x, y)
        plt.xlabel(infos["xlabel"])
        plt.ylabel(infos["ylabel"])
        plt.show()
        raw_input("Press Enter to close the plot window and continue...")
        plt.close()

def test02(nlevels):
    """ test get_map method """
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    fname = os.path.join(_curDir, 'specfiledata_test.dat')
    rngstr = '5:70'
    counter = 'arr_hdh_ene'
    motor = 'Spec.Energy'
    motor_counter = 'arr_xes_en'
    signal = 'zap_det_dtc'
    monitor = 'arr_I02sum'
    seconds = 'arr_seconds'
    norm = None #normalizing each scan does not make sense, the whole map has to be normalized!
    xystep = 0.05
    t = SpecfileData(fname)
    xcol, ycol, zcol = t.get_map(scans=rngstr, cntx=counter, cnty=motor, csig=signal, cmon=monitor, csec=seconds, norm=norm)
    etcol = xcol-ycol
    x, y, zz = t.grid_map(xcol, ycol, zcol, xystep=xystep)
    ex, et, ezz = t.grid_map(xcol, etcol, zcol, xystep=xystep)
    fig = plt.figure(num=test02.__doc__)
    ax = fig.add_subplot(121)
    ax.set_title('gridded data')
    cax = ax.contourf(x, y, zz, nlevels, cmap=cm.Paired_r)
    ax = fig.add_subplot(122)
    ax.set_title('energy transfer')
    cax = ax.contourf(ex, et, ezz, nlevels, cmap=cm.Paired_r)
    cbar = fig.colorbar(cax)
    plt.show()
    raw_input("Press Enter to close the plot and continue...")
    plt.close()

def test03():
    """ test get_mrg method """
    fname = os.path.join(_curDir, 'specfiledata_test.dat')
    signal = 'zap_det_dtc'
    monitor = 'arr_I02sum'
    seconds = 'arr_seconds'
    counter = 'arr_hdh_ene'
    motor = 'Spec.Energy'
    motor_counter = 'arr_xes_en'
    scans = '72, 74'
    t = SpecfileData(fname)
    for norm in [None, "area", "max-min", "sum"]:
        x, y = t.get_mrg(scans, cntx=counter, csig=signal, cmon=monitor, csec=seconds, norm=norm)
        print("Merged scans '{0}' with normalization {1}".format(scans, norm))
        import matplotlib.pyplot as plt
        plt.ion()
        plt.figure(num=test03.__doc__)
        plt.plot(x, y)
        plt.xlabel(counter)
        plt.ylabel("merged with norm {0}".format(norm))
        plt.show()
        raw_input("Press Enter to continue...")
        plt.close()

if __name__ == '__main__':
    #test01()
    #test02(100)
    #test03()
    pass
