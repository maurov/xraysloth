#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jupyter UI for Athena project files
-----------------------------------
"""

try:
    import ipywidgets as widgets
    from IPython.display import display
    HAS_IPYWIDGETS = True
except ImportError:
    HAS_IPYWIDGETS = False



def edit_athena_groups(aprj):
    """Edit AthenaGroup with Jupyter UI"""

    if HAS_IPYWIDGETS is False:
        raise ModuleNotFoundError("`ipywidgets` not installed")

    def _apply_edit_groups(event):
        """Overwrite _athena_groups dictionary with the modified keys/selection from the UI"""

        from collections import OrderedDict
        from copy import deepcopy

        newgroups = OrderedDict()
        for idx, (name, grp) in enumerate(aprj.groups.items()):
            gw = aprj._widgets[idx]
            if gw._changed is True:
                grp.sel = int(gw._newsel)
                newgroups[gw._newlab] = deepcopy(grp)
            else:
                newgroups[name] = deepcopy(grp)
        aprj.groups = newgroups
        print("Groups updated")

    # store initial labels and selections
    aprj._labs = [lab for lab in aprj.groups.keys()]
    aprj._sels = [grp.sel for grp in aprj.groups.values()]

    # store widgets
    aprj._widgets = [AthenaGroupWidget(idx, lab, grp.sel) for idx, (lab, grp) in enumerate(aprj.groups.items())]

    #make layout and display
    iLabs = [wdg.wlab for wdg in aprj._widgets]
    iSels = [wdg.wsel for wdg in aprj._widgets]
    vLabs = widgets.VBox(iLabs)
    vSels = widgets.VBox(iSels)
    hGrps = widgets.HBox([vLabs, vSels])
    tLabel = widgets.Label("Edit group names and selection (-> click 'Apply changes' once finished)")
    sButton = widgets.Button(description="Apply changes")
    sButton.on_click(_apply_edit_groups)

    editor = widgets.VBox([tLabel, hGrps, sButton])

    return display(editor)


class AthenaGroupWidget(object):

    def __init__(self, idx, lab, sel):

        self._changed = False
        self._idx = idx
        self._lab = lab
        self._sel = bool(sel)
        self._newlab = lab
        self._newsel = sel
        self.make_widget_label()
        self.make_widget_sel()

    def make_widget_label(self):
        self.wlab = widgets.Text(value=self._lab)
        self.wlab.observe(self.label_changed, 'value')

    def make_widget_sel(self):
        self.wsel = widgets.Checkbox(self._sel)
        self.wsel.observe(self.sel_changed, 'value')

    def label_changed(self, change):
        self._newlab = change.new
        self._changed = True
        # print(f"[{self._idx}] {self._lab} -> {self._newlab}") # DEBUG

    def sel_changed(self, change):
        self._newsel = change.new
        self._changed = True
        # print(f"[{self._idx}] {self._lab}: {self._sel} -> {self._newsel}") # DEBUG
