"""
Maze generator using recursive backtracking (iterative stack-based).

Generates a perfect maze (every cell reachable, exactly one path between
any two cells) on an odd-dimension grid.
"""

import numpy as np
import random


def generate_maze(rows: int = 21, cols: int = 21, seed: int = None) -> np.ndarray:
    """
    Generate a maze using iterative recursive backtracking.

    Args:
        rows: Number of rows (will be forced to odd).
        cols: Number of columns (will be forced to odd).
        seed: Optional random seed for reproducibility.

    Returns:
        np.ndarray of shape (rows, cols), values 0 (wall) or 1 (path).
        Start is at (0, 1), end is at (rows-1, cols-2).

    Raises:
        ValueError: If rows or cols < 5.
    """
    if rows < 5 or cols < 5:
        raise ValueError("Maze dimensions must be at least 5x5.")

    # Force odd dimensions
    rows = rows if rows % 2 == 1 else rows + 1
    cols = cols if cols % 2 == 1 else cols + 1

    if seed is not None:
        random.seed(seed)

    # Initialize grid: all walls
    grid = np.zeros((rows, cols), dtype=np.uint8)

    # Carving directions: each moves 2 cells (to skip wall between cells)
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    # Start carving from (1, 1)
    start_r, start_c = 1, 1
    grid[start_r, start_c] = 1

    stack = [(start_r, start_c)]

    while stack:
        cr, cc = stack[-1]

        # Find unvisited neighbors (2 cells away)
        unvisited = []
        for dr, dc in directions:
            nr, nc = cr + dr, cc + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and grid[nr, nc] == 0:
                unvisited.append((nr, nc, dr, dc))

        if unvisited:
            # Choose random unvisited neighbor
            nr, nc, dr, dc = random.choice(unvisited)

            # Carve wall between current and chosen cell
            grid[cr + dr // 2, cc + dc // 2] = 1
            grid[nr, nc] = 1

            stack.append((nr, nc))
        else:
            stack.pop()

    # Create entrance (top) and exit (bottom)
    grid[0, 1] = 1              # Start
    grid[rows - 1, cols - 2] = 1  # End

    return grid
