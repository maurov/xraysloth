#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple utility to convert Quantum ESPRESSO input files to XTL

..note:: The starting point of this code is `ase.io.espresso` from the
Atomic Simulation Environment (ASE) package.

"""
__author__ = "Mauro Rovezzi"
__email__ = "mauro.rovezzi@gmail.com"
__credits__ = "ASE developers (https://wiki.fysik.dtu.dk/ase/)"
__license__ = "BSD license <http://opensource.org/licenses/BSD-3-Clause>"
__organization__ = "European Synchrotron Radiation Facility"
__year__ = "2014-2015"

import numpy as np
from string import Template

#SOME CONSTANTS
# BOHR RADIUS IN ANGSTROMS
A0 = 0.5291772192

def read_fortran_namelist(fileobj):
    """Takes a fortran-namelist formatted file and returns appropriate
    dictionaries, followed by lines of text that do not fit this
    pattern.

    """
    data = {}
    extralines = []
    indict = False
    fileobj.seek(0)
    for line in fileobj.readlines():
        if indict and line.strip().startswith('/'):
            indict = False
        elif line.strip().startswith('&'):
            indict = True
            dictname = line.strip()[1:].lower()
            data[dictname] = {}
        elif (not indict) and (len(line.strip()) > 0):
            extralines.append(line)
        elif indict:
            key, value = line.strip().split('=')
            if value.endswith(','):
                value = value[:-1]
            value = value.strip()
            try:
                value = eval(value)
            except SyntaxError:
                value = {'.true.': True, '.false.': False}.get(value, value)
            data[dictname][key.strip()] = value
    return data, extralines


def f2f(value):
    """Converts a fortran-formatted double precision number (e.g.,
    2.323d2) to a python float. value should be a string.

    """
    value = value.replace('d', 'e')
    value = value.replace('D', 'e')
    return float(value)

def get_method(lines, line_no):
    """ Returns the method used in a given section """
    line = lines[line_no]
    if '{' in line:
        method = line[line.find('{') + 1:line.find('}')]
    elif '(' in line:
        method = line[line.find('(') + 1:line.find(')')]
    elif len(line.split()) == 2:
        method = line.split()[1]
    else:
        method = None
    return method

def get_cell(lines):
    """Returns the cell parameters from the lines of text of the espresso
    input file.

    """
    cell_params = []
    line = [n for (n, l) in enumerate(lines) if 'CELL_PARAMETERS' in l]
    if len(line) == 0:
        return None
    if len(line) > 1:
        raise RuntimeError('More than one CELL_PARAMETERS section?')
    line_no = line[0]
    for line in lines[line_no + 1:line_no + 4]:
        vx, vy, vz = line.split()
        cell_params.append([vx, vy, vz])
    return np.array(cell_params, dtype=np.float), get_method(lines, line_no)

def get_atoms(lines, n_atoms):
    """Returns the atomic positions of the atoms as an (ordered) list from
    the lines of text of the espresso input file.

    """
    atomic_positions = []
    line = [n for (n, l) in enumerate(lines) if 'ATOMIC_POSITIONS' in l]
    if len(line) == 0:
        return None
    if len(line) > 1:
        raise RuntimeError('More than one ATOMIC_POSITIONS section?')
    line_no = line[0]
    for line in lines[line_no + 1:line_no + n_atoms + 1]:
        #el, x, y, z = line.split()
        #atomic_positions.append([el, (f2f(x), f2f(y), f2f(z))])
        atomic_positions.append(line)
    return atomic_positions, get_method(lines, line_no)

def get_negative_pos(positions):
    """Returns the minimum negative atomic positions vector"""
    xnmin = 0.0
    ynmin = 0.0
    znmin = 0.0
    for line in positions:
        line_s = line.split()
        xnmin = min( xnmin, float(line_s[1]) ) 
        ynmin = min( ynmin, float(line_s[2]) ) 
        znmin = min( znmin, float(line_s[3]) ) 
    return xnmin, ynmin, znmin

def read_qe_in(fileobj):
    """Reads espresso input files."""
    if isinstance(fileobj, str):
        fileobj = open(fileobj, 'rU')
    # get data from qe input file
    data, extralines = read_fortran_namelist(fileobj)
    positions, method = get_atoms(extralines,
                                  n_atoms=data['system']['nat'])
    # init dictionary
    qedict = {}
    # cell
    if (data['system']['ibrav'] == 0):
        conv = float(data['system']['celldm(1)'])*A0
        v, cm = get_cell(extralines)
        ma = np.sqrt(v[0][0]**2 + v[0][1]**2 + v[0][2]**2)
        mb = np.sqrt(v[1][0]**2 + v[1][1]**2 + v[1][2]**2)
        mc = np.sqrt(v[2][0]**2 + v[2][1]**2 + v[2][2]**2)
        qedict.update({'alat' : ma * conv,
                       'blat' : mb * conv,
                       'clat' : mc * conv})
        dac = (v[0][0] * v[2][0] + v[0][1] * v[2][1] + v[0][2] * v[2][2])
        dbc = (v[1][0] * v[2][0] + v[1][1] * v[2][1] + v[1][2] * v[2][2])
        dab = (v[0][0] * v[1][0] + v[0][1] * v[1][1] + v[0][2] * v[1][2])
        cosac = dac / (ma * mc)
        cosbc = dbc / (mb * mc)
        cosab = dab / (ma * mb)
        qedict.update({'alpha' : np.rad2deg(np.arccos(cosac)),
                       'beta' : np.rad2deg(np.arccos(cosbc)),
                       'gamma' : np.rad2deg(np.arccos(cosab))})
    if (data['system']['ibrav'] == 4):
        qedict.update({'alat' : float(data['system']['celldm(1)']) * A0,
                       'blat' : float(data['system']['celldm(1)']) * A0,
                       'clat' : float(data['system']['celldm(3)']) * float(data['system']['celldm(1)']) * A0,
                       'alpha' : 90.0,
                       'beta' : 90.0,
                       'gamma' : 120.0})
    # atoms
    xn, yn, zn = get_negative_pos(positions)
    positions_str = ''
    positions_lst = []
    for line in positions:
        if ('angstrom' in method.lower()):
            line_s = line.split()
            line_s[1] = '{0:.7f}'.format( ( float(line_s[1]) - xn ) / float(qedict['alat']))
            line_s[2] = '{0:.7f}'.format( ( float(line_s[2]) - yn ) / float(qedict['blat']) )
            line_s[3] = '{0:.7f}'.format( ( float(line_s[3]) - zn ) / float(qedict['clat']) )
            line_s.append('\n')
            line = '   '.join(l for l in line_s)
        positions_lst.append(line.split())
        positions_str = positions_str+line
    #
    qedict.update({'atoms_lst' : positions_lst,
                   'atoms_str' : positions_str})
    fileobj.close()
    return qedict

def qe2xtl(fin, fout=None, title=None):
    """converts a QE input to XTL out file"""
    if fout is None:
        fout = '{0}.xtl'.format(fin.split('.')[0])
    dats = read_qe_in(fin)
    print('QE input: {0}\n'.format(fin))
    if title: dats.update({'title' : title})
    xtl_tmpl = Template('''
TITLE ${title}\n\
CELL\n\
 ${alat} ${blat} ${clat} ${alpha} ${beta} ${gamma}\n\
SYMMETRY NUMBER 1\n\
SYMMETRY LABEL P1\n\
ATOMS\n\
NAME   X   Y   Z\n\
${atoms_str}\
EOF
''')
    xtlout = xtl_tmpl.substitute(dats)
    f = open(fout, 'w')
    f.write(xtlout)
    f.close()
    print('XTL output: {0}\n'.format(fout))

if __name__ == '__main__':
    pass
