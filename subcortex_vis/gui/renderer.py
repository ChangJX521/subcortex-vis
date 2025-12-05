"""PyVista renderer for mesh visualization."""

from __future__ import annotations

from typing import List, Tuple, Dict, Optional

import pyvista as pv
from pyvistaqt import QtInteractor

from ..mesh_viz import _set_view


class MeshRenderer:
    """Handles PyVista mesh rendering with configurable lighting and styles.
    
    This class encapsulates all PyVista rendering logic, providing a clean
    interface for rendering meshes with different styles (3D shading, 2D flat).
    
    Attributes:
        plotter: The PyVista Qt interactor widget.
    """
    
    def __init__(self, plotter: QtInteractor):
        """Initialize the renderer.
        
        Args:
            plotter: The PyVista Qt interactor to render to.
        """
        self.plotter = plotter
        self.plotter.set_background("white")
    
    def render_meshes(
        self,
        label_meshes: List[Tuple[float, pv.PolyData]],
        label_colors: Dict[float, str],
        *,
        is_2d: bool = False,
        show_edges: bool = False,
        view: str = "left"
    ) -> None:
        """Render a list of labeled meshes.
        
        Args:
            label_meshes: List of (label, mesh) tuples to render.
            label_colors: Mapping from labels to hex color strings.
            is_2d: Whether to use 2D flat rendering style.
            show_edges: Whether to show mesh edges.
            view: View angle preset ('left', 'right', 'top', 'front', 'iso').
        """
        self._configure_projection(is_2d)
        self._clear_and_setup_lights()
        
        for idx, (lbl, mesh) in enumerate(label_meshes):
            color = label_colors.get(lbl, self._default_color(idx))
            self._add_mesh(mesh, color, is_2d, show_edges)
        
        self._apply_view(view)
    
    def _configure_projection(self, is_2d: bool) -> None:
        """Configure projection mode based on rendering style."""
        if is_2d:
            self.plotter.enable_parallel_projection()
            self.plotter.disable_anti_aliasing()
        else:
            self.plotter.disable_parallel_projection()
            self.plotter.enable_anti_aliasing()
    
    def _clear_and_setup_lights(self) -> None:
        """Clear the scene and set up lighting."""
        self.plotter.clear()
        self.plotter.renderer.lights.clear()
        
        # Three-point lighting setup
        self.plotter.add_light(
            pv.Light(position=(1, 1, 1), color="white", 
                    light_type="scene light", intensity=0.9)
        )
        self.plotter.add_light(
            pv.Light(position=(-1, -0.5, 1.5), color="white",
                    light_type="scene light", intensity=0.7)
        )
        self.plotter.add_light(
            pv.Light(position=(0, -1.5, -1), color="white",
                    light_type="scene light", intensity=0.5)
        )
    
    def _add_mesh(
        self, 
        mesh: pv.PolyData, 
        color: str, 
        is_2d: bool, 
        show_edges: bool
    ) -> None:
        """Add a single mesh to the scene.
        
        Args:
            mesh: The mesh to add.
            color: Hex color string for the mesh.
            is_2d: Whether to use 2D flat style.
            show_edges: Whether to show edges.
        """
        # Configure rendering parameters based on style
        if is_2d:
            ambient = 1.0
            diffuse = 0.1
            specular = 0.0
            lighting = False
            smooth_shading = False
            edge_display = False
        else:
            ambient = 0.25
            diffuse = 0.6
            specular = 0.15
            lighting = True
            smooth_shading = True
            edge_display = show_edges
        
        self.plotter.add_mesh(
            mesh,
            color=color,
            show_edges=edge_display,
            edge_color="#222222",
            line_width=1.0,
            smooth_shading=smooth_shading,
            specular=specular,
            specular_power=5,
            ambient=ambient,
            diffuse=diffuse,
            lighting=lighting,
            silhouette=None,
        )
    
    def _apply_view(self, view: str) -> None:
        """Apply view preset and reset camera."""
        _set_view(self.plotter, view)
        self.plotter.reset_camera()
        self.plotter.update()
    
    def reset_view(self, view: str) -> None:
        """Reset the camera to a specific view.
        
        Args:
            view: View angle preset.
        """
        if self.plotter.ren_win is None:
            return
        _set_view(self.plotter, view)
        self.plotter.reset_camera()
        self.plotter.update()
    
    def save_screenshot(self, path: str) -> bool:
        """Save a screenshot of the current view.
        
        Args:
            path: File path to save the screenshot.
            
        Returns:
            True if successful, False otherwise.
        """
        if self.plotter.ren_win is None:
            return False
        try:
            self.plotter.screenshot(path)
            return True
        except Exception:
            return False
    
    def clear(self) -> None:
        """Clear all meshes from the scene."""
        self.plotter.clear()
        self.plotter.update()
    
    @staticmethod
    def _default_color(idx: int) -> str:
        """Get default color for an index from the palette."""
        from .constants import PALETTE
        return PALETTE[idx % len(PALETTE)]
