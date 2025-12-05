"""File loading control panel widget."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Callable

from PyQt5 import QtWidgets


class FileLoaderPanel(QtWidgets.QWidget):
    """Panel for loading NIfTI files.
    
    Signals:
        file_loaded: Emitted when a file is successfully loaded.
    """
    
    def __init__(
        self, 
        parent: Optional[QtWidgets.QWidget] = None,
        default_path: str = "",
        on_load: Optional[Callable[[Path], None]] = None
    ):
        super().__init__(parent)
        self._on_load_callback = on_load
        self._setup_ui(default_path)
    
    def _setup_ui(self, default_path: str) -> None:
        """Set up the file loader UI components."""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_edit = QtWidgets.QLineEdit(default_path)
        self.file_edit.setPlaceholderText("Path to NIfTI file...")
        
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_file)
        
        load_btn = QtWidgets.QPushButton("Load NIfTI")
        load_btn.clicked.connect(self._load_file)
        
        layout.addWidget(self.file_edit)
        layout.addWidget(browse_btn)
        layout.addWidget(load_btn)
    
    def _browse_file(self) -> None:
        """Open file dialog to select a NIfTI file."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select NIfTI", "", "NIfTI (*.nii *.nii.gz)"
        )
        if path:
            self.file_edit.setText(path)
    
    def _load_file(self) -> None:
        """Trigger file loading."""
        path = Path(self.file_edit.text()).expanduser()
        if self._on_load_callback:
            self._on_load_callback(path)
    
    def get_path(self) -> Path:
        """Get the current file path."""
        return Path(self.file_edit.text()).expanduser()
    
    def set_path(self, path: str) -> None:
        """Set the file path."""
        self.file_edit.setText(path)
