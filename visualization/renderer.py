"""
Maze visualization renderer using matplotlib.

Produces figures showing the maze grid with overlays for visited cells,
frontier, current cell, and the solution path.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import COLORS


# Cell type constants for the overlay grid
_WALL = 0
_PATH = 1
_VISITED = 2
_FRONTIER = 3
_CURRENT = 4
_SOLUTION = 5
_START = 6
_END = 7

# Custom colormap based on cell types
_CMAP_COLORS = [
    COLORS["wall"],           # 0 - wall
    COLORS["path"],           # 1 - path
    COLORS["visited"],        # 2 - visited
    COLORS["frontier"],       # 3 - frontier
    COLORS["current"],        # 4 - current
    COLORS["solution_start"], # 5 - solution
    COLORS["start_cell"],     # 6 - start
    COLORS["end_cell"],       # 7 - end
]
_CMAP = mcolors.ListedColormap(_CMAP_COLORS)
_NORM = mcolors.BoundaryNorm(boundaries=range(len(_CMAP_COLORS) + 1), ncolors=len(_CMAP_COLORS))


def render_maze(grid: np.ndarray, start: tuple = None, end: tuple = None,
                figsize: tuple = None) -> Figure:
    """
    Render the base maze grid.

    Args:
        grid: 2D numpy array (0=wall, 1=path).
        start: (row, col) of start cell (highlighted green).
        end: (row, col) of end cell (highlighted red).
        figsize: Optional matplotlib figure size.

    Returns:
        matplotlib Figure.
    """
    display = grid.astype(np.float32).copy()

    if start is not None:
        display[start[0], start[1]] = _START
    if end is not None:
        display[end[0], end[1]] = _END

    fig, ax = _create_figure(display, figsize)
    ax.set_title("Maze", fontsize=14, fontweight="bold", pad=10)
    return fig


def render_step(grid: np.ndarray, step, start: tuple = None,
                end: tuple = None, figsize: tuple = None) -> Figure:
    """
    Render a single algorithm step with overlays.

    Args:
        grid: 2D maze grid.
        step: algorithms.base.SolveStep instance.
        start: Start position.
        end: End position.
        figsize: Optional figure size.

    Returns:
        matplotlib Figure.
    """
    display = grid.astype(np.float32).copy()

    # Layer visited cells
    for r, c in step.visited:
        if display[r, c] == _PATH:
            display[r, c] = _VISITED

    # Layer frontier cells
    for r, c in step.frontier:
        if display[r, c] == _PATH or display[r, c] == _VISITED:
            display[r, c] = _FRONTIER

    # Current cell
    cr, cc = step.current
    display[cr, cc] = _CURRENT

    # Start and end markers
    if start is not None:
        display[start[0], start[1]] = _START
    if end is not None:
        display[end[0], end[1]] = _END

    fig, ax = _create_figure(display, figsize)

    info_text = f"Visited: {len(step.visited)}  |  Frontier: {len(step.frontier)}"
    ax.set_title(info_text, fontsize=11, pad=8)

    return fig


def render_solution(grid: np.ndarray, path: list, start: tuple = None,
                    end: tuple = None, figsize: tuple = None) -> Figure:
    """
    Render the maze with the solution path highlighted.

    Args:
        grid: 2D maze grid.
        path: List of (row, col) tuples forming the solution.
        start: Start position.
        end: End position.
        figsize: Optional figure size.

    Returns:
        matplotlib Figure.
    """
    display = grid.astype(np.float32).copy()

    for r, c in path:
        display[r, c] = _SOLUTION

    if start is not None:
        display[start[0], start[1]] = _START
    if end is not None:
        display[end[0], end[1]] = _END

    fig, ax = _create_figure(display, figsize)
    ax.set_title(f"Solution Path (length: {len(path)})",
                 fontsize=14, fontweight="bold", pad=10)
    return fig


def render_comparison_chart(results: dict) -> Figure:
    """
    Create a comparison bar chart for multiple algorithm results.

    Args:
        results: dict mapping algorithm name → AlgorithmResult.

    Returns:
        matplotlib Figure with subplots for time, nodes, memory.
    """
    names = list(results.keys())
    times = [results[n].stats.get("time_ms", 0) for n in names]
    nodes = [results[n].stats.get("nodes_explored", 0) for n in names]
    memory = [results[n].stats.get("memory_kb", 0) for n in names]
    path_lens = [results[n].stats.get("path_length", 0) for n in names]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    fig.patch.set_facecolor("#0e1117")

    bar_colors = ["#4fc3f7", "#ab47bc", "#ff7043"]

    metrics = [
        (times, "Time (ms)", "Execution Time"),
        (nodes, "Count", "Nodes Explored"),
        (memory, "KB", "Peak Memory"),
        (path_lens, "Steps", "Path Length"),
    ]

    for ax, (values, ylabel, title) in zip(axes, metrics):
        bars = ax.bar(names, values, color=bar_colors[:len(names)],
                      edgecolor="white", linewidth=0.5, alpha=0.85)
        ax.set_ylabel(ylabel, fontsize=10, color="white")
        ax.set_title(title, fontsize=12, fontweight="bold", color="white", pad=8)
        ax.set_facecolor("#1a1a2e")
        ax.tick_params(colors="white", labelsize=9)
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Value labels on bars
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{val:.1f}" if isinstance(val, float) else str(val),
                    ha="center", va="bottom", fontsize=9, color="white",
                    fontweight="bold")

    fig.tight_layout(pad=2)
    return fig


# ── Internal Helpers ──────────────────────────────────────────────

def _create_figure(display: np.ndarray, figsize: tuple = None):
    """Create a styled matplotlib figure from a display grid."""
    rows, cols = display.shape
    if figsize is None:
        scale = max(4, min(10, max(rows, cols) / 8))
        figsize = (scale, scale * rows / cols)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    fig.patch.set_facecolor("#0e1117")

    ax.imshow(display, cmap=_CMAP, norm=_NORM, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#0e1117")

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout(pad=0.5)
    return fig, ax
