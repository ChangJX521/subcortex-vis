"""Rendering parameters control panel widget."""

from __future__ import annotations

from typing import Optional, Callable

from PyQt5 import QtWidgets

from ..constants import DEFAULT_SIGMA, DEFAULT_SMOOTH_ITER


class RenderParamsPanel(QtWidgets.QWidget):
    """Panel for mesh rendering parameters.
    
    This widget provides controls for:
    - Gaussian smoothing sigma
    - Mesh smoothing iterations
    - Edge visibility
    - Rendering style (3D/2D)
    - View angle selection
    """
    
    def __init__(
        self, 
        parent: Optional[QtWidgets.QWidget] = None,
        on_param_changed: Optional[Callable[[], None]] = None,
        on_view_changed: Optional[Callable[[str], None]] = None
    ):
        super().__init__(parent)
        self._on_param_changed = on_param_changed
        self._on_view_changed = on_view_changed
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the parameters panel UI components."""
        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Sigma (Gaussian smoothing)
        self.sigma_spin = QtWidgets.QDoubleSpinBox()
        self.sigma_spin.setRange(0.0, 5.0)
        self.sigma_spin.setSingleStep(0.1)
        self.sigma_spin.setValue(DEFAULT_SIGMA)
        self.sigma_spin.valueChanged.connect(self._on_change)
        layout.addRow("Sigma:", self.sigma_spin)
        
        # Smooth iterations
        self.smooth_spin = QtWidgets.QSpinBox()
        self.smooth_spin.setRange(0, 200)
        self.smooth_spin.setValue(DEFAULT_SMOOTH_ITER)
        self.smooth_spin.valueChanged.connect(self._on_change)
        layout.addRow("Smooth iter:", self.smooth_spin)
        
        # Show edges checkbox
        self.edges_chk = QtWidgets.QCheckBox("Show edges")
        self.edges_chk.setChecked(False)
        self.edges_chk.stateChanged.connect(self._on_change)
        layout.addRow(self.edges_chk)
        
        # Rendering style
        self.style_combo = QtWidgets.QComboBox()
        self.style_combo.addItems(["3D shading", "2D flat"])
        self.style_combo.currentTextChanged.connect(self._on_change)
        layout.addRow("Style:", self.style_combo)
        
        # View angle
        self.view_combo = QtWidgets.QComboBox()
        self.view_combo.addItems(["left", "right", "top", "front", "iso"])
        self.view_combo.currentTextChanged.connect(self._on_view_change)
        layout.addRow("View:", self.view_combo)
    
    def _on_change(self) -> None:
        """Handle parameter change."""
        if self._on_param_changed:
            self._on_param_changed()
    
    def _on_view_change(self, view: str) -> None:
        """Handle view angle change."""
        if self._on_view_changed:
            self._on_view_changed(view)
    
    @property
    def sigma(self) -> float:
        """Get current sigma value."""
        return self.sigma_spin.value()
    
    @property
    def smooth_iter(self) -> int:
        """Get current smooth iterations value."""
        return self.smooth_spin.value()
    
    @property
    def show_edges(self) -> bool:
        """Get current show edges setting."""
        return self.edges_chk.isChecked()
    
    @property
    def style(self) -> str:
        """Get current rendering style."""
        return self.style_combo.currentText()
    
    @property
    def is_2d(self) -> bool:
        """Check if 2D flat style is selected."""
        return self.style == "2D flat"
    
    @property
    def view(self) -> str:
        """Get current view angle."""
        return self.view_combo.currentText()
