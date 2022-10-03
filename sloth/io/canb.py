import os
import logging
import tempfile
import matplotlib.pyplot as plt
from matplotlib import cm

from plotly.subplots import make_subplots
import plotly.graph_objects as go

from larch import Group
from larch.io import AthenaProject
from larch.io.specfile_reader import DataSourceSpecH5
from larch.xafs import pre_edge, autobk

from sloth.utils.strings import str2rng
from sloth.utils.matplotlib import get_colors

def canb2athena(fname, scans=None, datadir=None, save=True, **kws):
    '''convert ESRF-BM30 multi-element fluorescence channels Spec file (aka 'canb') to an Athena project''' 

    sx_logger = logging.getLogger("silx")
    sx_logger.setLevel(logging.ERROR)

    verbose = kws.get("verbose", False)

    if datadir is None:
        fname_split = fname.split(os.sep)
        fname = fname_split[-1]
        datadir = os.sep.join(fname_split[:-1])
    
    try:
        fnodot = fname.split('.')[0]
    except Exception:
        fnodot = fname
    
    if isinstance(save, str):
        fnprj = os.path.join(datadir, save)
    else:
        fnprj = os.path.join(datadir, f"{fnodot}.prj")

    if os.path.isfile(fnprj):
        os.remove(fnprj)

    apj = AthenaProject(fnprj)
    apj.info = {}
    
    d = DataSourceSpecH5(os.path.join(datadir, fname), verbose=verbose)
    
    if scans is None:
        scans = d.get_scans()
    else:
        scans = str2rng(scans)
        print(f"Loaded scans: {scans}")
        
    apj.info['scans'] = scans
    apj.info['cnts'] = []
    
    #load data into Larch group
    for iscan, scan in enumerate(scans):
        try:
            scan_no = scan[0]
            scan_label = f"scan{scan_no.replace('.', '_')}" #Larch group names cannot contain .
        except Exception:
            scan_no = scan
            scan_label = f"scan{scan}"

        d.set_scan(scan_no)

        ene = d.get_array("Energy") * 1000
        norm = d.get_array("I0")
        bad_channels = []
            
        for cnt in d.get_counters():
            if 't' in cnt:
                continue
            if cnt in ['I0', 'T', 'Energy']:
                continue
            mu = d.get_array(cnt)
            g = Group(id=f"{scan_label}_{cnt}", datatype='xas', energy=ene, mu=mu, i0=norm)
            try:
                pre_edge(g)
                #autobk(g) #slow
                apj.add_group(g)
                apj.info['cnts'].append(cnt)
            except:
                #print(f"skipped {cnt} (-> bad_channels)")
                bad_channels.append(cnt)
                pass
              
    if save:
        apj.save()
        print(f"data saved to:  {fnprj}")
        
    return apj


def plot_canb(apj):
    scans = apj.info['scans']
    cnts = apj.info['cnts']
    
    fig = make_subplots(rows=len(scans), cols=1, subplot_titles=[f"scan {scan[0]}" for scan in scans])

    yshift=0
    for ig, (gid, g) in enumerate(apj.groups.items()):
        
        fig.add_trace(
            go.Scatter(x=g.energy, y=g.norm+yshift, name=cnts[ig], marker=None),
                row=1, col=1
            )
        yshift += 0.1
        
    fig.update_layout(height=800, width=1000, title_text=f"{file_in}")
    fig.show()

    return fig