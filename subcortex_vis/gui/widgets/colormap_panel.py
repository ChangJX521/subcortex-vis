"""Colormap control panel widget."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Callable, Dict

from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from ..constants import COLORMAPS


class ColormapPanel(QtWidgets.QGroupBox):
    """Panel for ROI value loading and colormap configuration.
    
    This widget provides controls for:
    - Loading ROI values from CSV/TXT files
    - Selecting and previewing colormaps
    - Configuring colormap range (vmin/vmax)
    
    Signals:
        values_loaded: Emitted when ROI values are loaded.
        colormap_changed: Emitted when colormap settings change.
    """
    
    # Qt signals
    values_loaded = QtCore.pyqtSignal(dict)  # Emits label_values dict
    colormap_changed = QtCore.pyqtSignal()
    values_cleared = QtCore.pyqtSignal()
    
    def __init__(
        self, 
        parent: Optional[QtWidgets.QWidget] = None,
        on_values_loaded: Optional[Callable[[Dict[float, float]], None]] = None,
        on_colormap_changed: Optional[Callable[[], None]] = None
    ):
        super().__init__("ROI Values & Colormap", parent)
        
        self._on_values_loaded = on_values_loaded
        self._on_colormap_changed = on_colormap_changed
        
        self.label_values: Dict[float, float] = {}
        self.use_colormap = False
        self.current_colormap = "viridis"
        self.colormap_vmin: Optional[float] = None
        self.colormap_vmax: Optional[float] = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the colormap panel UI components."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # File input
        self.value_file_edit = QtWidgets.QLineEdit()
        self.value_file_edit.setPlaceholderText("Click to select CSV/TXT file...")
        self.value_file_edit.setReadOnly(True)
        self.value_file_edit.mousePressEvent = lambda e: self._browse_value_file()
        self.value_file_edit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        layout.addWidget(self.value_file_edit)
        
        # Action buttons
        btn_row = QtWidgets.QHBoxLayout()
        load_btn = QtWidgets.QPushButton("Load")
        load_btn.clicked.connect(self._load_values)
        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_values)
        btn_row.addWidget(load_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        # Colormap controls
        cmap_row = QtWidgets.QHBoxLayout()
        self.use_cmap_chk = QtWidgets.QCheckBox("Use colormap")
        self.use_cmap_chk.setChecked(False)
        self.use_cmap_chk.stateChanged.connect(self._on_colormap_toggle)
        cmap_row.addWidget(self.use_cmap_chk)
        
        cmap_row.addWidget(QtWidgets.QLabel("Colormap:"))
        self.cmap_combo = QtWidgets.QComboBox()
        self.cmap_combo.addItems(COLORMAPS)
        self.cmap_combo.currentTextChanged.connect(self._on_colormap_selection_changed)
        cmap_row.addWidget(self.cmap_combo)
        layout.addLayout(cmap_row)
        
        # Range controls
        range_row = QtWidgets.QHBoxLayout()
        range_row.addWidget(QtWidgets.QLabel("Range:"))
        
        self.vmin_spin = QtWidgets.QDoubleSpinBox()
        self.vmin_spin.setRange(-1e6, 1e6)
        self.vmin_spin.setDecimals(3)
        self.vmin_spin.setValue(0.0)
        self.vmin_spin.setSpecialValueText("Auto")
        self.vmin_spin.valueChanged.connect(self._on_range_changed)
        range_row.addWidget(QtWidgets.QLabel("Min:"))
        range_row.addWidget(self.vmin_spin)
        
        self.vmax_spin = QtWidgets.QDoubleSpinBox()
        self.vmax_spin.setRange(-1e6, 1e6)
        self.vmax_spin.setDecimals(3)
        self.vmax_spin.setValue(1.0)
        self.vmax_spin.setSpecialValueText("Auto")
        self.vmax_spin.valueChanged.connect(self._on_range_changed)
        range_row.addWidget(QtWidgets.QLabel("Max:"))
        range_row.addWidget(self.vmax_spin)
        
        auto_btn = QtWidgets.QPushButton("Auto")
        auto_btn.clicked.connect(self.auto_range)
        range_row.addWidget(auto_btn)
        layout.addLayout(range_row)
        
        # Colorbar preview
        self.colorbar_label = QtWidgets.QLabel()
        self.colorbar_label.setFixedHeight(30)
        self.colorbar_label.setStyleSheet("border: 1px solid #555;")
        layout.addWidget(self.colorbar_label)
        
        self._update_colorbar_preview()
    
    def _browse_value_file(self) -> None:
        """Open file dialog to select ROI values file."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select ROI Values CSV", "", 
            "CSV (*.csv);;Text (*.txt);;All (*.*)"
        )
        if path:
            self.value_file_edit.setText(path)
    
    def _load_values(self) -> None:
        """Load ROI values from file."""
        import csv
        
        path = Path(self.value_file_edit.text()).expanduser()
        if not path.exists():
            return
        
        try:
            self.label_values.clear()
            
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                
                # Detect column indices
                label_col = 0
                value_col = 1
                
                if header:
                    header_lower = [h.lower().strip() for h in header]
                    for i, h in enumerate(header_lower):
                        if h in ('label', 'roi', 'region', 'id', 'index'):
                            label_col = i
                        if h in ('value', 'score', 'overlap', 'weight', 'magnitude'):
                            value_col = i
                    
                    # Check if first row is data
                    try:
                        float(header[label_col])
                        float(header[value_col])
                        lbl = float(header[label_col])
                        val = float(header[value_col])
                        self.label_values[lbl] = val
                    except (ValueError, IndexError):
                        pass
                
                for row in reader:
                    if len(row) < 2:
                        continue
                    try:
                        lbl = float(row[label_col])
                        val = float(row[value_col])
                        self.label_values[lbl] = val
                    except (ValueError, IndexError):
                        continue
            
            if not self.label_values:
                return
            
            self.auto_range()
            self.values_loaded.emit(self.label_values)
            
            if self._on_values_loaded:
                self._on_values_loaded(self.label_values)
                
        except Exception:
            pass
    
    def _clear_values(self) -> None:
        """Clear loaded values."""
        self.label_values.clear()
        self.use_cmap_chk.setChecked(False)
        self.value_file_edit.clear()
        self.values_cleared.emit()
    
    def _on_colormap_toggle(self, state: int) -> None:
        """Handle colormap checkbox toggle."""
        self.use_colormap = state == QtCore.Qt.Checked
        self._emit_colormap_changed()
    
    def _on_colormap_selection_changed(self, cmap_name: str) -> None:
        """Handle colormap selection change."""
        self.current_colormap = cmap_name
        self._update_colorbar_preview()
        if self.use_colormap:
            self._emit_colormap_changed()
    
    def _on_range_changed(self) -> None:
        """Handle range spinbox changes."""
        self.colormap_vmin = self.vmin_spin.value()
        self.colormap_vmax = self.vmax_spin.value()
        self._update_colorbar_preview()
        if self.use_colormap:
            self._emit_colormap_changed()
    
    def _emit_colormap_changed(self) -> None:
        """Emit colormap changed signal."""
        self.colormap_changed.emit()
        if self._on_colormap_changed:
            self._on_colormap_changed()
    
    def auto_range(self) -> None:
        """Auto-detect range from loaded values."""
        if not self.label_values:
            return
        
        values = list(self.label_values.values())
        vmin = min(values)
        vmax = max(values)
        margin = (vmax - vmin) * 0.05 if vmax > vmin else 0.1
        
        self.vmin_spin.setValue(vmin - margin)
        self.vmax_spin.setValue(vmax + margin)
        self._update_colorbar_preview()
    
    def _update_colorbar_preview(self) -> None:
        """Update the colorbar preview image."""
        try:
            cmap = plt.get_cmap(self.current_colormap)
            gradient = np.linspace(0, 1, 256).reshape(1, -1)
            gradient = np.vstack([gradient] * 20)
            
            colors = cmap(gradient)
            colors_rgb = (colors[:, :, :3] * 255).astype(np.uint8)
            
            height, width = colors_rgb.shape[:2]
            bytes_per_line = 3 * width
            qimage = QtGui.QImage(
                colors_rgb.data, width, height, bytes_per_line, 
                QtGui.QImage.Format_RGB888
            )
            pixmap = QtGui.QPixmap.fromImage(qimage)
            
            scaled = pixmap.scaled(
                self.colorbar_label.width() - 2,
                self.colorbar_label.height() - 2,
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.colorbar_label.setPixmap(scaled)
        except Exception:
            pass
    
    def get_color_for_value(self, value: float) -> str:
        """Get hex color for a value using current colormap settings."""
        cmap = plt.get_cmap(self.current_colormap)
        vmin = self.colormap_vmin if self.colormap_vmin is not None else 0
        vmax = self.colormap_vmax if self.colormap_vmax is not None else 1
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        rgba = cmap(norm(value))
        return mcolors.to_hex(rgba[:3])
    
    def compute_colors(self, labels: list) -> Dict[float, str]:
        """Compute colors for all labels based on their values."""
        colors = {}
        for lbl in labels:
            if lbl in self.label_values:
                colors[lbl] = self.get_color_for_value(self.label_values[lbl])
        return colors
