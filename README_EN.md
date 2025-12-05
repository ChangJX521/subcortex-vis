# Subcortex Mesh Viewer

English | [中文](README.md)

A lightweight tool for importing NIfTI (`.nii/.nii.gz`) volumetric data, extracting meshes via marching cubes, and visualizing them in PyVista. The implementation is based on the logic in `subcortex_regional_overlap.ipynb`.

## Dependencies

- Python 3.9+
- `pyvista`, `nibabel`, `numpy`, `scipy`
- GUI additionally requires: `PyQt5`, `pyvistaqt`, `matplotlib`

Installation:
```bash
pip install pyvista nibabel numpy scipy PyQt5 pyvistaqt matplotlib
```

## Project Structure

```
subcortex-vis/
├── subcortex_vis/              # Main Python package
│   ├── __init__.py
│   ├── mesh_viz.py             # Core mesh extraction & visualization
│   └── gui/                    # GUI subpackage
│       ├── __init__.py         # Exports MeshGui, main, etc.
│       ├── __main__.py         # Enables python -m subcortex_vis.gui
│       ├── constants.py        # Color palettes, colormaps, defaults
│       ├── delegates.py        # Custom Qt delegate (color squares)
│       ├── renderer.py         # PyVista rendering logic
│       ├── main_window.py      # Main window MeshGui class
│       └── widgets/            # Reusable UI components
│           ├── __init__.py
│           ├── file_loader.py      # File loading panel
│           ├── label_list.py       # Label list panel
│           ├── colormap_panel.py   # ROI values & colormap panel
│           └── render_params.py    # Rendering parameters panel
├── scripts/
│   ├── gui_app.py              # GUI entry point
│   └── demo_mesh.py            # Command-line demo script
├── atlas/                      # Atlas files
├── data/                       # Sample data
└── Tian2020MSA/                # Tian subcortex atlas
```

## Quick Start

### Command Line Mode

Generate a left-view screenshot using the Tian subcortex template:
```bash
python -m subcortex_vis.mesh_viz \
  --input atlas/Tian_Subcortex_S2_3T.nii.gz \
  --label 1 \
  --sigma 0.8 \
  --smooth-iter 30 \
  --view left \
  --screenshot plots/demo_mesh.png
```

Parameters:
- `--label`: Extract a specific label (uses mask with 0.5 isosurface by default). If omitted, use `--threshold` for grayscale isosurface extraction.
- `--sigma`: Gaussian smoothing before marching cubes.
- `--smooth-iter`/`--smooth-relax`: Mesh smoothing parameters.
- `--view`: View preset - `iso|left|right|top|front`.
- `--screenshot`: When provided, renders offscreen and saves; otherwise opens interactive window.

### As Python Functions

```python
from subcortex_vis.mesh_viz import load_nii_volume, extract_isosurface, visualize_mesh

volume, spacing, origin = load_nii_volume("atlas/Tian_Subcortex_S2_3T.nii.gz")
mask = (volume == 1).astype(float)
mesh = extract_isosurface(mask, spacing, origin, threshold=0.5, sigma=0.8, smooth_iter=30)
visualize_mesh(mesh, view="left", background="white")
```

## GUI Application

Features: Load NIfTI files, auto-list non-zero labels, multi-select ROIs, custom colors, import ROI values with colormap support, adjust smoothing parameters, switch views, and save screenshots.

### Launch Methods

```bash
# Method 1: Via script
python scripts/gui_app.py

# Method 2: As module
python -m subcortex_vis.gui
```

### Interface Features

| Section | Description |
|---------|-------------|
| **File Loading** | Select `.nii/.nii.gz` file, click "Load NIfTI" to auto-detect labels |
| **Label List** | Multi-select ROIs, click "Set color" for custom colors |
| **ROI Values & Colormap** | Import CSV to assign values, enable colormap for auto-coloring |
| **Render Parameters** | Adjust Sigma, Smooth iter, show edges, 2D/3D style |
| **View Control** | left/right/top/front/iso view presets |
| **Export** | Reset view, Save screenshot as PNG |

### ROI Values File Format

Supports CSV or TXT format with two columns: label and value. Auto-detects common column names:

```csv
label,value
1,0.523
2,0.187
3,0.891
...
```

### Using GUI Components in Code

```python
from subcortex_vis.gui import MeshGui, PALETTE, COLORMAPS
from subcortex_vis.gui.renderer import MeshRenderer
from subcortex_vis.gui.widgets import LabelListPanel, ColormapPanel

# Create main window
gui = MeshGui()
gui.show()
```

## License

See [Tian2020MSA/license.txt](Tian2020MSA/license.txt) for the Tian atlas license.
