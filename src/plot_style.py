"""Shared matplotlib style so every figure in the repo looks the same."""

import matplotlib.pyplot as plt

# Fixed colour order: the same signal always gets the same colour across figures.
COLORS = {
    "soma": "#2a78d6",      # somatic voltage / spikes (blue)
    "input": "#eb6834",     # injected current (orange)
    "adapt": "#1baf7a",     # adaptation current w (aqua)
    "dendrite": "#6250d6",  # dendritic voltage, used from notebook 02 on (violet)
    "alt": "#eda100",       # comparison condition, e.g. adaptation off (yellow)
}
INK = "#0b0b0b"
INK_SOFT = "#52514e"
GRID = "#e4e3df"


def apply_style():
    plt.rcParams.update({
        "figure.dpi": 110,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": INK_SOFT,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "xtick.color": INK_SOFT,
        "ytick.color": INK_SOFT,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "lines.linewidth": 1.6,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "font.size": 10,
    })
