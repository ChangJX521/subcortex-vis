#!/usr/bin/env python
"""Entry point for the subcortex mesh visualization GUI.

This script provides a command-line entry point for launching the
GUI application. The actual implementation is in the subcortex_vis.gui package.

Usage:
    python scripts/gui_app.py
    
    # Or from the package:
    python -m subcortex_vis.gui
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running directly from repo without installation
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from subcortex_vis.gui import main


if __name__ == "__main__":
    main()
