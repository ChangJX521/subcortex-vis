"""Custom Qt delegates for the GUI."""

from __future__ import annotations

from typing import Dict, Optional

from PyQt5 import QtCore, QtWidgets, QtGui


class ColorSquareDelegate(QtWidgets.QStyledItemDelegate):
    """Custom delegate to draw a color square at the right side of each ROI item.
    
    This delegate displays a colored square next to each item in the list,
    representing the current color assigned to that ROI label.
    
    Attributes:
        label_colors: Mapping from label values to hex color strings.
        label_values: Mapping from label values to their associated numeric values.
    """
    
    SQUARE_SIZE = 16
    MARGIN = 4
    
    def __init__(
        self, 
        parent: Optional[QtWidgets.QWidget] = None, 
        label_colors: Optional[Dict[float, str]] = None, 
        label_values: Optional[Dict[float, float]] = None
    ):
        super().__init__(parent)
        self.label_colors = label_colors or {}
        self.label_values = label_values or {}
    
    def paint(
        self, 
        painter: QtGui.QPainter, 
        option: QtWidgets.QStyleOptionViewItem, 
        index: QtCore.QModelIndex
    ) -> None:
        """Draw the default item and a color square on the right."""
        # Draw the default item first
        super().paint(painter, option, index)
        
        # Get the label from UserRole
        lbl = index.data(QtCore.Qt.UserRole)
        if lbl is None:
            return
        
        # Draw color square on the right
        color_hex = self.label_colors.get(lbl, "#cccccc")
        
        rect = option.rect
        square_rect = QtCore.QRect(
            rect.right() - self.SQUARE_SIZE - self.MARGIN,
            rect.top() + (rect.height() - self.SQUARE_SIZE) // 2,
            self.SQUARE_SIZE,
            self.SQUARE_SIZE
        )
        
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setBrush(QtGui.QColor(color_hex))
        painter.setPen(QtGui.QPen(QtGui.QColor("#555555"), 1))
        painter.drawRoundedRect(square_rect, 2, 2)
        painter.restore()
    
    def sizeHint(
        self, 
        option: QtWidgets.QStyleOptionViewItem, 
        index: QtCore.QModelIndex
    ) -> QtCore.QSize:
        """Return size hint with extra space for the color square."""
        size = super().sizeHint(option, index)
        size.setWidth(size.width() + self.SQUARE_SIZE + self.MARGIN * 2)
        return size
    
    def update_colors(
        self, 
        label_colors: Dict[float, str], 
        label_values: Optional[Dict[float, float]] = None
    ) -> None:
        """Update the color and value mappings.
        
        Args:
            label_colors: New mapping from labels to colors.
            label_values: Optional new mapping from labels to values.
        """
        self.label_colors = label_colors
        if label_values is not None:
            self.label_values = label_values
