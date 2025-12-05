"""GUI package for subcortex mesh visualization.

This package provides a PyQt5-based graphical interface for loading,
viewing, and customizing subcortical brain mesh visualizations.

Modules:
    constants: Color palettes, colormaps, and UI constants.
    delegates: Custom Qt item delegates for the label list.
    renderer: PyVista mesh rendering logic.
    main_window: Main GUI window class.
    widgets: Reusable UI widget components.

Usage:
    from subcortex_vis.gui import MeshGui, main
    
    # Run the application
    main()
    
    # Or create the widget manually
    gui = MeshGui()
    gui.show()
"""

from .main_window import MeshGui, main
from .constants import PALETTE, COLORMAPS
from .renderer import MeshRenderer

__all__ = [
    "MeshGui",
    "main",
    "PALETTE",
    "COLORMAPS",
    "MeshRenderer",
]
