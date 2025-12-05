"""Main window for the subcortex mesh visualization GUI."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Dict, List

from PyQt5 import QtCore, QtWidgets
from pyvistaqt import QtInteractor

from ..mesh_viz import extract_label_meshes, load_nii_volume
from .constants import (
    CONTROL_PANEL_MAX_WIDTH, 
    CONTROL_PANEL_MIN_WIDTH, 
    RENDER_DEBOUNCE_MS,
    PALETTE,
)
from .widgets import FileLoaderPanel, LabelListPanel, ColormapPanel, RenderParamsPanel
from .renderer import MeshRenderer


class MeshGui(QtWidgets.QWidget):
    """Main GUI window for subcortex mesh visualization.
    
    This widget provides a complete interface for loading NIfTI files,
    selecting and coloring ROIs, and rendering 3D/2D mesh visualizations.
    
    Attributes:
        volume: The loaded NIfTI volume data.
        spacing: Voxel spacing from the NIfTI file.
        origin: Volume origin from the NIfTI file.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Subcortex Mesh Viewer")
        self.resize(1400, 900)
        
        # Data state
        self.volume = None
        self.spacing = None
        self.origin = None
        
        # Render debouncing
        self._render_timer = QtCore.QTimer()
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._render_scene)
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the main UI layout."""
        main_layout = QtWidgets.QHBoxLayout(self)
        
        # Controls panel
        controls_widget = self._build_controls_panel()
        main_layout.addWidget(controls_widget, stretch=0)
        
        # Plot widget
        self.plotter = QtInteractor(self)
        self.renderer = MeshRenderer(self.plotter)
        main_layout.addWidget(self.plotter.interactor, stretch=3)
    
    def _build_controls_panel(self) -> QtWidgets.QWidget:
        """Build the left-side controls panel."""
        controls_widget = QtWidgets.QWidget()
        controls_widget.setMaximumWidth(CONTROL_PANEL_MAX_WIDTH)
        controls_widget.setMinimumWidth(CONTROL_PANEL_MIN_WIDTH)
        
        controls = QtWidgets.QVBoxLayout(controls_widget)
        controls.setSpacing(8)
        controls.setContentsMargins(5, 5, 5, 5)
        
        # File loader
        default_path = str(Path("atlas") / "Tian_Subcortex_S2_3T.nii.gz")
        self.file_loader = FileLoaderPanel(
            parent=self,
            default_path=default_path,
            on_load=self._load_volume
        )
        controls.addWidget(self.file_loader)
        
        # Label list
        self.label_list = LabelListPanel(
            parent=self,
            on_color_change=self._on_color_change
        )
        self.label_list.item_changed.connect(self._schedule_render)
        controls.addWidget(self.label_list, stretch=1)
        
        # Separator
        controls.addWidget(self._create_separator())
        
        # Colormap panel
        self.colormap_panel = ColormapPanel(
            parent=self,
            on_values_loaded=self._on_values_loaded,
            on_colormap_changed=self._on_colormap_changed
        )
        self.colormap_panel.values_cleared.connect(self._on_values_cleared)
        controls.addWidget(self.colormap_panel)
        
        # Render parameters
        self.render_params = RenderParamsPanel(
            parent=self,
            on_param_changed=self._schedule_render,
            on_view_changed=self._on_view_changed
        )
        controls.addWidget(self.render_params)
        
        # Action buttons
        action_row = QtWidgets.QHBoxLayout()
        
        reset_btn = QtWidgets.QPushButton("Reset view")
        reset_btn.clicked.connect(self._reset_view)
        
        screenshot_btn = QtWidgets.QPushButton("Save screenshot")
        screenshot_btn.clicked.connect(self._save_screenshot)
        
        action_row.addWidget(reset_btn)
        action_row.addWidget(screenshot_btn)
        controls.addLayout(action_row)
        
        # Status label
        self.status_lbl = QtWidgets.QLabel("Load a NIfTI to begin.")
        controls.addWidget(self.status_lbl)
        controls.addStretch()
        
        return controls_widget
    
    def _create_separator(self) -> QtWidgets.QFrame:
        """Create a horizontal separator line."""
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        return line
    
    # === Data Loading ===
    
    def _load_volume(self, path: Path) -> None:
        """Load a NIfTI volume file.
        
        Args:
            path: Path to the NIfTI file.
        """
        if not path.exists():
            self._set_status(f"File not found: {path}")
            return
        
        try:
            self.volume, self.spacing, self.origin = load_nii_volume(path)
        except Exception as exc:
            self._set_status(f"Failed to load: {exc}")
            return
        
        # Extract unique labels
        labels = sorted({float(v) for v in self.volume.flatten() if v != 0})
        
        # Populate label list
        self.label_list.populate_labels(
            labels, 
            values=self.colormap_panel.label_values
        )
        
        self._set_status(f"Loaded {path.name}; found {len(labels)} labels.")
        self._render_scene()
    
    # === Color Management ===
    
    def _on_color_change(self, labels: List[float], color_hex: str) -> None:
        """Handle color change for selected labels.
        
        Args:
            labels: Labels whose color was changed.
            color_hex: New hex color string.
        """
        self._schedule_render()
        self._set_status(f"Set color {color_hex} for {len(labels)} ROI(s).")
    
    def _on_values_loaded(self, values: Dict[float, float]) -> None:
        """Handle ROI values loaded from file.
        
        Args:
            values: Mapping from labels to values.
        """
        self.label_list.set_label_values(values)
        self._update_colors_from_colormap()
        self._set_status(f"Loaded {len(values)} ROI values.")
        self._schedule_render()
    
    def _on_values_cleared(self) -> None:
        """Handle ROI values cleared."""
        # Reset colors to default palette
        for i, lbl in enumerate(self.label_list.get_checked_labels()):
            self.label_list.label_colors[lbl] = PALETTE[i % len(PALETTE)]
        
        self.label_list.set_label_values({})
        self._set_status("ROI values cleared.")
        self._schedule_render()
    
    def _on_colormap_changed(self) -> None:
        """Handle colormap settings change."""
        self._update_colors_from_colormap()
        self._schedule_render()
    
    def _update_colors_from_colormap(self) -> None:
        """Update label colors based on colormap settings."""
        if not self.colormap_panel.use_colormap:
            # Reset to default palette
            for i in range(len(self.label_list.label_colors)):
                labels = list(self.label_list.label_colors.keys())
                for idx, lbl in enumerate(labels):
                    self.label_list.label_colors[lbl] = PALETTE[idx % len(PALETTE)]
        else:
            # Apply colormap colors
            labels = list(self.label_list.label_colors.keys())
            new_colors = self.colormap_panel.compute_colors(labels)
            self.label_list.set_label_colors(new_colors)
    
    # === Rendering ===
    
    def _schedule_render(self) -> None:
        """Schedule a render with debouncing."""
        if self.volume is None:
            return
        self._render_timer.start(RENDER_DEBOUNCE_MS)
    
    def _render_scene(self) -> None:
        """Render the current scene."""
        if self.volume is None:
            self._set_status("Load a NIfTI first.")
            return
        
        labels = self.label_list.get_checked_labels()
        if not labels:
            self.renderer.clear()
            self._set_status("No labels selected.")
            return
        
        # Extract meshes
        sigma = self.render_params.sigma
        smooth_iter = self.render_params.smooth_iter
        
        label_meshes = extract_label_meshes(
            self.volume, labels, self.spacing, self.origin,
            sigma=sigma, smooth_iter=smooth_iter, threshold=0.5
        )
        
        if not label_meshes:
            self.renderer.clear()
            self._set_status("No meshes extracted with current settings.")
            return
        
        # Render meshes
        self.renderer.render_meshes(
            label_meshes,
            self.label_list.label_colors,
            is_2d=self.render_params.is_2d,
            show_edges=self.render_params.show_edges,
            view=self.render_params.view
        )
        
        self._set_status(f"Rendered {len(label_meshes)} meshes.")
    
    # === View Controls ===
    
    def _on_view_changed(self, view: str) -> None:
        """Handle view angle change.
        
        Args:
            view: New view angle preset.
        """
        self._reset_view()
    
    def _reset_view(self) -> None:
        """Reset the camera view."""
        self.renderer.reset_view(self.render_params.view)
    
    def _save_screenshot(self) -> None:
        """Save a screenshot of the current view."""
        if self.plotter.ren_win is None:
            self._set_status("Nothing to capture. Render first.")
            return
        
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save screenshot", "screenshot.png", "PNG (*.png)"
        )
        if not path:
            return
        
        if self.renderer.save_screenshot(path):
            self._set_status(f"Saved screenshot: {path}")
        else:
            self._set_status("Failed to save screenshot.")
    
    # === Status ===
    
    def _set_status(self, text: str) -> None:
        """Update the status label.
        
        Args:
            text: Status message to display.
        """
        self.status_lbl.setText(text)
        self.status_lbl.repaint()


def main() -> None:
    """Run the GUI application."""
    app = QtWidgets.QApplication(sys.argv)
    gui = MeshGui()
    gui.show()
    sys.exit(app.exec_())
