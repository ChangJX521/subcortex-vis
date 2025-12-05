"""Label list widget for ROI selection."""

from __future__ import annotations

from typing import List, Dict, Optional, Callable, Set

from PyQt5 import QtCore, QtWidgets, QtGui

from ..delegates import ColorSquareDelegate
from ..constants import PALETTE


class LabelListPanel(QtWidgets.QWidget):
    """Panel for displaying and selecting ROI labels.
    
    This widget provides a list of ROI labels with checkboxes for selection
    and color squares showing the assigned colors.
    
    Signals:
        selection_changed: Emitted when the selection changes.
        item_changed: Emitted when an item's check state changes.
    """
    
    # Qt signals
    selection_changed = QtCore.pyqtSignal()
    item_changed = QtCore.pyqtSignal()
    
    def __init__(
        self, 
        parent: Optional[QtWidgets.QWidget] = None,
        on_color_change: Optional[Callable[[List[float], str], None]] = None
    ):
        super().__init__(parent)
        self.label_colors: Dict[float, str] = {}
        self.label_values: Dict[float, float] = {}
        self._on_color_change = on_color_change
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the label list UI components."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header label
        layout.addWidget(QtWidgets.QLabel("Labels (non-zero):"))
        
        # List widget with custom delegate
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        
        self.color_delegate = ColorSquareDelegate(
            self.list_widget, self.label_colors, self.label_values
        )
        self.list_widget.setItemDelegate(self.color_delegate)
        
        # Connect signals
        self.list_widget.itemChanged.connect(self._on_item_changed)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.list_widget, stretch=1)
        
        # Button row
        btn_row = QtWidgets.QHBoxLayout()
        
        select_all_btn = QtWidgets.QPushButton("Select all")
        select_all_btn.clicked.connect(self.select_all)
        
        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_selection)
        
        color_btn = QtWidgets.QPushButton("Set color")
        color_btn.clicked.connect(self._choose_color)
        
        btn_row.addWidget(select_all_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(color_btn)
        layout.addLayout(btn_row)
        
        # Color preview
        preview_row = QtWidgets.QHBoxLayout()
        preview_row.addWidget(QtWidgets.QLabel("Selected color:"))
        
        self.color_preview = QtWidgets.QLabel()
        self.color_preview.setFixedSize(40, 20)
        self.color_preview.setStyleSheet("background: #cccccc; border: 1px solid #555;")
        
        preview_row.addWidget(self.color_preview)
        preview_row.addStretch()
        layout.addLayout(preview_row)
    
    def _on_item_changed(self) -> None:
        """Handle item check state change."""
        self.item_changed.emit()
    
    def _on_selection_changed(self) -> None:
        """Handle list selection change."""
        self.selection_changed.emit()
        self._update_color_preview()
    
    def _update_color_preview(self) -> None:
        """Update the color preview based on current selection."""
        highlighted = self.get_highlighted_labels()
        if highlighted:
            color_hex = self.label_colors.get(highlighted[0], "#cccccc")
            self._set_preview_color(color_hex)
        else:
            self._set_preview_color("#cccccc")
    
    def _set_preview_color(self, color_hex: str) -> None:
        """Set the preview label's background color."""
        self.color_preview.setStyleSheet(f"background: {color_hex}; border: 1px solid #555;")
    
    def _choose_color(self) -> None:
        """Open color dialog for selected labels."""
        highlighted = self.get_highlighted_labels()
        if not highlighted:
            return
        
        initial = self.label_colors.get(highlighted[0], "#4C78A8")
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(initial), self, "Choose color")
        
        if not color.isValid():
            return
        
        color_hex = color.name()
        for lbl in highlighted:
            self.label_colors[lbl] = color_hex
        
        self._set_preview_color(color_hex)
        self.list_widget.viewport().update()
        
        if self._on_color_change:
            self._on_color_change(highlighted, color_hex)
    
    def populate_labels(
        self, 
        labels: List[float], 
        values: Optional[Dict[float, float]] = None
    ) -> None:
        """Populate the list with labels.
        
        Args:
            labels: List of label values to display.
            values: Optional mapping of labels to their numeric values.
        """
        self.list_widget.clear()
        self.label_colors.clear()
        
        if values:
            self.label_values = values
        
        for idx, lbl in enumerate(labels):
            # Format display text
            display_text = f"{lbl:.0f}"
            if lbl in self.label_values:
                display_text += f" ({self.label_values[lbl]:.3f})"
            
            item = QtWidgets.QListWidgetItem(display_text)
            item.setData(QtCore.Qt.UserRole, lbl)
            item.setCheckState(QtCore.Qt.Checked)
            
            # Assign default color
            color_hex = self._get_default_color(idx)
            self.label_colors[lbl] = color_hex
            
            self.list_widget.addItem(item)
        
        # Update delegate
        self.color_delegate.update_colors(self.label_colors, self.label_values)
        self.list_widget.viewport().update()
    
    def refresh_display(self) -> None:
        """Refresh the list display with updated values."""
        # Store current check states
        checked_labels: Set[float] = set()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            lbl = item.data(QtCore.Qt.UserRole)
            if item.checkState() == QtCore.Qt.Checked:
                checked_labels.add(lbl)
        
        # Get all labels
        labels = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            labels.append(item.data(QtCore.Qt.UserRole))
        
        # Rebuild list
        self.list_widget.clear()
        for idx, lbl in enumerate(labels):
            display_text = f"{lbl:.0f}"
            if lbl in self.label_values:
                display_text += f" ({self.label_values[lbl]:.3f})"
            
            item = QtWidgets.QListWidgetItem(display_text)
            item.setData(QtCore.Qt.UserRole, lbl)
            item.setCheckState(
                QtCore.Qt.Checked if lbl in checked_labels else QtCore.Qt.Unchecked
            )
            self.list_widget.addItem(item)
        
        self.color_delegate.update_colors(self.label_colors, self.label_values)
    
    def _get_default_color(self, idx: int) -> str:
        """Get default color for an index."""
        return PALETTE[idx % len(PALETTE)]
    
    def select_all(self) -> None:
        """Check all items in the list."""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(QtCore.Qt.Checked)
    
    def clear_selection(self) -> None:
        """Uncheck all items in the list."""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(QtCore.Qt.Unchecked)
    
    def get_checked_labels(self) -> List[float]:
        """Get list of labels that are checked (for rendering)."""
        labels: List[float] = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                lbl = item.data(QtCore.Qt.UserRole)
                if lbl is not None:
                    labels.append(float(lbl))
        return labels
    
    def get_highlighted_labels(self) -> List[float]:
        """Get list of labels that are highlighted/selected (for color setting)."""
        labels: List[float] = []
        for item in self.list_widget.selectedItems():
            lbl = item.data(QtCore.Qt.UserRole)
            if lbl is not None:
                labels.append(float(lbl))
        return labels
    
    def set_label_colors(self, colors: Dict[float, str]) -> None:
        """Update label colors and refresh display."""
        self.label_colors.update(colors)
        self.color_delegate.update_colors(self.label_colors, self.label_values)
        self.list_widget.viewport().update()
    
    def set_label_values(self, values: Dict[float, float]) -> None:
        """Update label values and refresh display."""
        self.label_values = values
        self.color_delegate.label_values = values
        self.refresh_display()
