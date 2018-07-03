#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CIFreader utility class based on PyCifRW library

"""

import os, sys
import re
import logging

_logger = logging.getLogger(__name__)

HAS_CifFile = False
try:
    import CifFile
    HAS_CifFile = True
except ImportError:
    pass

class CIFSymmetry(object):
    def __init__(self):
        self.no = None
        self.name = None
        self.type = None
        self.xyz = None
        self.xyz_id = None

class CIFAtom(object):
    def __init__(self):
        self.site_H = None
        self.B_iso = None
        self.label = None
        self.label2 = None
        self.occupancy = None
        self.fract_x = None
        self.fract_y = None
        self.fract_z = None
        self.oxid_no = None
        #### gives 4a or 8c, etc.
        self.symm_multi = None
        self.symm_wyckoff = None

class CIFCitation(object):
    def __init__(self):
        self.year = None
        self.author = None
        self.journal = None
        self.journal_id = None
        self.title = None
        self.id = None
        self.volume = None
        self.first_page = None
        self.last_page = None

class CIFReader(object):
    """CIF reader utility"""

    def __init__(self):
        """init"""
        pass

    def read_cif(self, cif_fname):
        """read CIF file

        Parameters
        ----------

        cif_fname: str
            CIF file name

        """

        if not HAS_CifFile:
            _logger.error('CifFile not found! (is PyCifRW installed?)')
            return

        self.cif_fname = cif_fname

        try:
            self.cf = CifFile.ReadCif(cif_fname)
        except:
            self.cf = None
            return

        self.key = self.cf.keys()[0]
        print('Read key: {0}'.format(self.key))


    def get_subkey(self, k):
        """returns subkey"""
        try:
            return self.cf[self.key][k]
        except:
            return None

    def get_all_keys(self):
        """all subkeys"""
        return self.cf[self.key].keys()
        
    def get_label(self):
        """label"""
        return self.get_subkey('_chemical_name_common')
              
    def get_cell(self):
        """get cell parameters

        Returns
        =======

        cell: list
              ['_cell_length_a', '_cell_length_b', '_cell_length_c',\
               '_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma']

        
        """
        _keys = ('_cell_length_a', '_cell_length_b', '_cell_length_c',\
                 '_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma')
        cell = []
        for key in _keys:
            kval = float(self.get_subkey(key))
            cell.append(kval)
        return cell

    def get_atoms(self):
        """get atoms list

        Returns
        =======

        atoms: list

        
        """
        _keys = ('_atom_site_type_symbol', '_atom_site_label',\
                 '_atom_site_fract_x', '_atom_site_fract_y', '_atom_site_fract_z',\
                 '_atom_site_occupancy')
        atoms_kvals = []
        natoms = len(self.get_subkey(_keys[0]))
        for key in _keys:
            if ('_atom_site_fract_' in key) or ('_atom_site_occupancy' in key):
                kval = [float(nstr) for nstr in self.get_subkey(key)]
            else:
                kval = self.get_subkey(key)
            atoms_kvals.append(kval)
        #reshape
        atoms = []
        atline = []
        for ati in range(natoms):
            for atk in atoms_kvals:
                atline.append(atk[ati])
            atoms.append(atline)
            atline = []

        return atoms

def readCifFile(cifFile):
    """read CIF file with PyCifRW

    Forked from: https://github.com/danmichaelo/cif2vasp/blob/master/cif2vasp.py

    ##################################
    .. warning:: BUGGY, NOT WORKING!!!
    ##################################
    
    """
    if not HAS_CifFile:
        _logger.error('CifFile not found (is PyCifRW installed?)')
        return

    if not os.path.exists(cifFile):
        raise IOError("CIF file '%s' was not found!" % (cifFile))
    
    cf = CifFile.CifFile(cifFile)
    print("------------------------------------------------------------------")
    if len(cf) != 1:
        raise StandardError("The cif file contains %i data blocks, while one was expected")
        # A cif file can contain several "datablocks" that each start
        # with "data_".
    
    cb = cf[cf.keys()[0]]                               # open the first block
    AA = float(re.match('([0-9.]*)',cb['_cell_length_a']).group(0))
    BB = float(re.match('([0-9.]*)',cb['_cell_length_b']).group(0))
    CC = float(re.match('([0-9.]*)',cb['_cell_length_c']).group(0))
    alpha = float(cb['_cell_angle_alpha'])
    beta = float(cb['_cell_angle_beta'])
    gamma = float(cb['_cell_angle_gamma'])
    SG = int(cb['_symmetry_Int_Tables_number'])              # spacegroup
  
    atomTypes = []
    atoms = ''
    fracOccFound = False
    firstAtom = True
    atoms = []
    for atom in cb.GetLoop('_atom_site_label'):
        atomKeys = dir(atom)
        if '_atom_site_type_symbol' in atomKeys:
            m = re.match('[a-z]*',atom._atom_site_type_symbol,re.I)
            atomType = m.group(0)
        else:
            m = re.match('[a-z]*',atom._atom_site_label,re.I)
            atomType = m.group(0)
        
        atomLabel = atom._atom_site_label

        if '_atom_site_occupancy' in atomKeys:
            occ = float(atom._atom_site_occupancy)
            if not occ == 1.0:
                if not fracOccFound: print(" ")
                print("  WARNING: Fractional occupancy (" + str(occ) +") " \
                      + "found for atom of type " + atomType + ".")
                fracOccFound = True
        else:
            occ = 1.0
        
        # Some crystal structures obtained by neutron diffraction use D for H:
        if atomType == 'D':
            atomType = 'H'
            atomLabel.replace('H','D')
        
        if ('_atom_site_symmetry_multiplicity' in atomKeys) and ('_atom_site_Wyckoff_symbol' in atomKeys):
            atomTypes.append(atomType+' at '+atom._atom_site_symmetry_multiplicity+atom._atom_site_Wyckoff_symbol)
        else:
            atomTypes.append(atomType)
        
        atomPos = [atom._atom_site_fract_x, atom._atom_site_fract_y, atom._atom_site_fract_z]
        for p in atomPos:
            pp = p.split(".")
            if len(pp) is 2:
                decimals = p.split(".")[1]
                if len(decimals) > 3 and len(decimals) < 6 and decimals[0] == decimals[1] and decimals[-1] != "0":
                    print("\n---------------------\n"\
                          +"  Warning: If the fractional coordinate "+p\
                          +"  is a recurring decimal, such as 1/3,\n" \
                          +"  then it is necessary to specify this value to six decimal places to be sure of \n" \
                          +" it being recognised correctly as a spcecial position.\n  ------------------")
		
		# The coordinates of the atom (_atom_site_fract_x/y/z) may have 
		# a last digit in parenthesis, like "0.6636(7)". Therefore we
		# extract the part consisting of only digits and a decimal separator:
                p = re.compile('[0-9.]*')
        atomX = float(p.match(atom._atom_site_fract_x).group())
        atomY = float(p.match(atom._atom_site_fract_y).group())
        atomZ = float(p.match(atom._atom_site_fract_z).group())
        
        #atoms += "%s %f %f %f %f %f\n" % (atomType, atomX, atomY, atomZ, 0.0, occ)
        atoms.append({'label': atomLabel, 'type': atomType, 'pos': (atomX,atomY,atomZ) })
        firstAtom = False

    if fracOccFound: 
        print(" ")
        print("ERROR: Fractional occupancies are not currently supported.\n")
        exit()
    
        print("Atom types: " + ', '.join(atomTypes))
    
    return {'spacegroup': SG,
            'unit_cell': [AA,BB,CC,alpha,beta,gamma],
            'scatterers': atoms}
    
if __name__ == '__main__':
    mycif = 'LaFeSi_small.cif' #TODO: put an example CIF file in resources
    mylabel = mycif.split('.')[0]
    if 0:
        c = CIFReader()
        c.read_cif(mycif)
        print('Label: {0}'.format(c.get_label()))
        print('---')
        print('Cell: {0}'.format(c.get_cell()))
        print('---')
        print('Atoms:\n {0}'.format(c.get_atoms()))
    if 0:
        ### NOT WORKING ###
        lfs = readCifFile(mycif)
    if 0:
        #from ASE
        from ase import io
        ats = io.read(mycif)
    if 1:
        #http://pymatgen.org/_modules/pymatgen/cli/feff_input_generation.html#main
        from pymatgen.io.feff.sets import (FEFFDictSet, MPXANESSet, MPEXAFSSet)
        from pymatgen.io.feff.inputs import (get_atom_map, get_absorbing_atom_symbol_index)
        from pymatgen.io.cif import CifParser

        r = CifParser(mycif)
        calc_type = 'EXAFS' #'XANES'
        if calc_type == 'EXAFS':
            calc_set = MPEXAFSSet
        else:
            calc_set = MPXANESSet


        myexa = {'EDGE': 'K',
                 'S02': 0.01,
                 'CONTROL': '1 1 1 1 1 1',
                 'PRINT': '1 0 0 0 0 0',
                 'EXCHANGE' : 0,
                 'SCF': '4.5 0 30 .2 1',
                 'RPATH': 8,
                 'EXAFS': 20,
                 'NLEG' : 4,
                 'SIG2' : 0.005,
                 'COREHOLE': 'FSR'}

        abs_el = 'Fe'
        abs_at = 5
        
        struct = r.get_structures()[0]
        _edge = 'K'
        _radius = 8.5
        _comm = 'Feff from CIF file with pymatgen'

        pmg = calc_set(abs_at, struct, edge=_edge, radius=_radius,\
                       user_tag_settings=myexa)

        out_dir = '{0}_{1}'.format(mylabel, 'test') 
        pmg.write_input(output_dir=out_dir)
        
        feff = pmg.all_input()
        ats = pmg.atoms.get_lines()
                       
    #EOF                   
    pass
                       
