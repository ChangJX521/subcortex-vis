"""Constants for the GUI application."""

# Default color palette for ROI visualization
PALETTE = [
    "#4C78A8",
    "#E45756",
    "#72B7B2",
    "#F28E2B",
    "#59A14F",
    "#B279A2",
    "#FF9DA6",
    "#9C755F",
]

# Available colormaps for value-based coloring
COLORMAPS = [
    "viridis", "plasma", "inferno", "magma", "cividis",
    "Reds", "Blues", "Greens", "Oranges", "Purples",
    "RdBu", "RdYlBu", "RdYlGn", "Spectral", "coolwarm",
    "hot", "cool", "spring", "summer", "autumn", "winter",
    "YlOrRd", "YlGnBu", "PuBuGn", "BuPu", "GnBu",
]

# Default mesh rendering parameters
DEFAULT_SIGMA = 0.8
DEFAULT_SMOOTH_ITER = 30
DEFAULT_THRESHOLD = 0.5

# UI constants
CONTROL_PANEL_MAX_WIDTH = 320
CONTROL_PANEL_MIN_WIDTH = 280
RENDER_DEBOUNCE_MS = 80
