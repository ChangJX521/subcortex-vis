"""Lightweight helpers for loading NIfTI volumes and visualizing subcortical meshes.

This package provides tools for:
- Loading NIfTI neuroimaging files
- Extracting isosurfaces from volumetric data
- Visualizing subcortical brain structures
- Interactive GUI for mesh visualization

Modules:
    mesh_viz: Core mesh extraction and visualization functions.
    gui: PyQt5-based graphical user interface.
"""

from .mesh_viz import (
    load_nii_volume,
    extract_isosurface,
    visualize_mesh,
)

__all__ = [
    "load_nii_volume",
    "extract_isosurface",
    "visualize_mesh",
]
