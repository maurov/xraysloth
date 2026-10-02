# CLAUDE.md — xraysloth

xraysloth is a **public** GitHub repository. Keep tracked files (code, docs, this file,
commit messages) free of details about private projects; private context lives in
`CLAUDE.local.md` (gitignored, loaded automatically when present).

## What this repository is today

Sloth is Mauro's old repository of codes and ideas. Most of it has since been propagated
to other projects, among them the public **xraylarch** (XAS analysis; received sloth's
io/math/rixs code), **larixite** (crystal structures and clusters for XAS: CIF, FDMNES
inputs) and **famewoks** (BM16/BM30 workflows, BLISS → Larch), plus some private ones
(see `CLAUDE.local.md`). The old `sloth/gui/daxs` lives on as the separate daxs project.

Nowadays sloth is used for:

1. creating the personal Python development environment (`binder/environment.yml`,
   env name `sloth2507`, plus `binder/requirements-*.txt`);
2. a few functions imported by beamline notebooks for BM16 (spectrometer alignment);
3. keeping the old work on raytracing spectrometers in Rowland circle geometry.

## Refactoring plan (proposed 2026-10-02, not started)

Goal: split sloth into three clearly separated things:

1. **`binder/`** — the development environment as the main product of the repo. The folder
   name stays `binder/`: BinderHub (repo2docker) only reads `binder/`, `.binder/` or the repo
   root, and ignores root files when `binder/` exists.
2. **`sloth` library** — small, tested, containing only what is unique and still used:
   crystal/Bragg math, X-ray line data, Rowland geometry, the BM16 spectrometer model,
   peak fitting used for spectrometer alignment.
3. **`archive/`** — raytracing (SHADOW3/ShadowOui) and old examples, not packaged/linted.

### Findings that motivate it

- No other package depends on sloth; its only users are BM16 beamline notebooks.
- Imports still used by current notebooks, and where they should come from:

  | sloth import | target |
  |---|---|
  | `sloth.io.datasource_spech5.DataSourceSpecH5` | `larch.io.specfile_reader.DataSourceSpecH5` (larch lacks `get_curves/get_mrg/get_stack/view`) |
  | `sloth.utils.arrays.merge_arrays_1d` | `larch.io.mergegroups.merge_arrays_1d` |
  | `sloth.utils.strings.str2rng` | `larch.io.str2rng` |
  | `sloth.utils.strings.natural_keys` | `larch.io.specfile_reader.natural_keys` |
  | `sloth.collects.datagroup_rixs.RixsDataPlotter` | `larch.plot.plot_rixsdata.RixsDataPlotter` (same methods) |
  | `sloth.fit.peakfit_silx.fit_splitpvoigt` | keep → `sloth.fit.peaks` |
  | `sloth.utils.bragg` (`SI_ALAT, GE_ALAT, d_cubic, kev2ang, ang2kev, findhkl, get_dspacing`) | keep → `sloth.crystals` |
  | `sloth.utils.xdata` (`fluo_width, xray_line, xray_edge, find_line, get_element`) | keep → `sloth.xdata` |
  | `sloth.inst.rowland.RcHoriz` | keep → `sloth.rowland.geometry` |
  | `sloth.inst.spectro14` (`show_spectro_overview, rotation_matrix`) | keep → `sloth.bm16.spectro14` |
  | `sloth.utils.matplotlib.get_colors` | tiny helper or palettable |

- Already moved elsewhere (drop from sloth):
  `io/*`, `math/*`, `groups/*` → xraylarch; `collects/*` (deprecated);
  `workflows/bliss2larch_fluo.py` → famewoks `bliss2larch.py`;
  `calculators/fdmnes.py`, `io/cif_reader.py` → larixite;
  `gui/*` → daxs. Check `io/canb.py` before dropping.
- `sloth/raytracing` uses only SHADOW3 (`import Shadow`) and ShadowOui/PyQt4; nothing uses
  shadow4 even though `binder/requirements-oasys.txt` installs it.

### Target layout

```
xraysloth/
├── binder/                 # stays here for BinderHub (repo2docker)
│   ├── environment.yml     # + apt.txt, postBuild (BinderHub)
│   ├── requirements-*.txt  # larch, jupyter, nexus, ewoks, doc, dev (oasys/xrt → archive?)
│   ├── devstack.txt        # -e ../xraylarch -e ../larixite -e ../famewoks -e ..
│   └── make_env.sh         # create/update env, pip install -e devstack.txt
│                           # (+ devstack.local.txt if present, gitignored)
├── src/sloth/
│   ├── __init__.py         # version only (drop NullClass, __pkgs__)
│   ├── crystals.py         # ← utils/bragg
│   ├── xdata.py            # ← utils/xdata (xraydb only; drop xraylib/PyMca/GUI imports)
│   ├── rowland/geometry.py # ← inst/rowland (rotations via numpy or larch.math.transformations)
│   ├── rowland/dthetaxz.py # ← inst/dthetaxz + dthetaxz_plot
│   ├── bm16/spectro14.py   # ← inst/spectro14
│   ├── fit/peaks.py        # ← fit/peakfit_silx (+ peakfit_lmfit if still used)
│   └── _compat.py          # temporary re-exports (step 4)
├── tests/                  # crystals, xdata, rowland, spectro14 with known values
├── archive/                # raytracing/, examples/, macros/, data/ — not packaged
├── notebooks/  docs/
└── pyproject.toml          # deps: numpy, scipy, matplotlib, xraydb, silx (no pymca/xraylib)
```

### Migration steps

1. Tag current state `v25.1-legacy` (archived notebooks pin to it).
2. Reorganize `binder/` in place (do not rename it: BinderHub needs it): add `devstack.txt`
   + `make_env.sh`, clean up the requirements files. (Independent of the rest.)
   BinderHub builds see only this repo, so `devstack.txt` is for local env creation;
   `make_env.sh` also reads the gitignored `binder/devstack.local.txt` when present.
3. Restructure to `src/` layout with the kept modules; remove PyQt4/xraylib/PyMca
   dependencies from them; add real tests.
4. Add compatibility shims for one release (`sloth.io.datasource_spech5`,
   `sloth.utils.{strings,arrays,bragg,xdata}`, `sloth.inst.*`, `sloth.fit.peakfit_silx`)
   re-exporting from larch / new locations with a `DeprecationWarning`.
5. Update imports in the current beamline notebooks (scriptable from the table above);
   archived notebooks stay on the legacy tag. Paths are in `CLAUDE.local.md`.
6. Drop shims and dead modules, move raytracing to `archive/`, release `26.x`.

### Open decisions (ask Mauro before starting)

1. Raytracing: archive in-repo (recommended), legacy tag only, or port to shadow4 as its own project?
2. Environment scope: one superset env with all side projects editable, or a base that
   per-project envs (e.g. `famewoks262`) extend?
3. Upstream `fit_splitpvoigt` and Bragg/crystal math to xraylarch instead of keeping them?
4. Keep the name `sloth` for the library, or rename it (e.g. `rowland`, `bm16spectro`) and
   keep "sloth" for the environment?

## State before the refactoring (done 2026-10-02)

Commits `7ec8ca1`..`4c93389`: CI moved to GitHub Actions, RTD/Sphinx modernized, packaging
fixed (`GPL-3.0-or-later`), Python 2 leftovers removed, f-strings, raw strings for LaTeX,
undefined names fixed, `utils/xafsplots.py` and scipy.weave code removed.

Known remaining issues: 7 modules fail to import (`io.rixs_aps_gsecars`,
`raytracing.{shadow_spectro1,shadowoui_plotter,shadowoui_screens,shadowoui_spectro1}`,
`utils.ipylarch`, `utils.jupyter`); the test suite is a single version test;
`sloth/examples` is a symlink to `examples/`.

## Working conventions

- Dev env: `~/local/miniforge/envs/sloth2507` (Python 3.12).
- Checks: `ruff check sloth`, `python -m pytest sloth/test`, `python -m build` + `twine check`.
- Do not commit unless asked (see global instructions).
