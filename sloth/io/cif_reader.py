#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CIFreader utility class based on PyCifRW library

"""

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
            print('PyCifRW not found!')
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
            
if __name__ == '__main__':
    c = CIFReader()
    c.read_cif('LaFeSi_small.cif')
    print('Label: {0}'.format(c.get_label()))
    print('---')
    print('Cell: {0}'.format(c.get_cell()))
    print('---')
    print('Atoms:\n {0}'.format(c.get_atoms()))
    pass
