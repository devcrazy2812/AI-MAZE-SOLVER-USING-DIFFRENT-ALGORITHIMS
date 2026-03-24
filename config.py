"""
Maze Solver AI Visualization - Configuration
"""

# ─── Upload Constraints ───────────────────────────────────────────
MAX_UPLOAD_SIZE_MB = 5
SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg", ".bmp"]
MAX_MAZE_DIMENSION = 501  # max rows/cols for generated mazes

# ─── Default Maze Generation ─────────────────────────────────────
DEFAULT_MAZE_ROWS = 21
DEFAULT_MAZE_COLS = 21

# ─── Algorithm Choices ────────────────────────────────────────────
ALGORITHMS = {
    "BFS (Breadth-First Search)": "bfs",
    "DFS (Depth-First Search)": "dfs",
    "A* Search": "astar",
}

HEURISTICS = {
    "Manhattan": "manhattan",
    "Euclidean": "euclidean",
}

# ─── Visualization Colors (RGBA 0-1 for matplotlib) ──────────────
COLORS = {
    "wall": (0.12, 0.12, 0.15, 1.0),
    "path": (0.97, 0.97, 0.98, 1.0),
    "visited": (0.35, 0.55, 0.90, 0.6),
    "frontier": (1.0, 0.85, 0.25, 0.8),
    "current": (0.95, 0.25, 0.25, 1.0),
    "solution_start": (0.15, 0.75, 0.35, 1.0),
    "solution_end": (0.90, 0.15, 0.20, 1.0),
    "start_cell": (0.10, 0.80, 0.30, 1.0),
    "end_cell": (0.90, 0.10, 0.10, 1.0),
}

# ─── Animation ────────────────────────────────────────────────────
DEFAULT_ANIMATION_SPEED_MS = 50
MIN_ANIMATION_SPEED_MS = 10
MAX_ANIMATION_SPEED_MS = 500
ANIMATION_STEP_SKIP = 1  # render every Nth step for large mazes
