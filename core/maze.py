"""
Maze representation using numpy grid.

Grid convention:
    0 = wall
    1 = open path
Start = first open cell in row 0
End   = first open cell in last row
"""

import numpy as np
from PIL import Image
from pathlib import Path


class MazeError(Exception):
    """Base exception for maze-related errors."""
    pass


class InvalidImageError(MazeError):
    """Raised when the input image is invalid or unreadable."""
    pass


class NoStartEndError(MazeError):
    """Raised when no start or end position can be found."""
    pass


class Maze:
    """
    Numpy-based maze representation.

    Attributes:
        grid (np.ndarray): 2D array, 0=wall, 1=path.
        start (tuple[int, int]): (row, col) of the start cell.
        end (tuple[int, int]): (row, col) of the end cell.
        rows (int): Number of rows.
        cols (int): Number of columns.
    """

    def __init__(self, grid: np.ndarray, start: tuple, end: tuple):
        if grid.ndim != 2:
            raise MazeError("Grid must be a 2D numpy array.")
        if not self._is_valid_pos(grid, start):
            raise MazeError(f"Start position {start} is outside the grid or on a wall.")
        if not self._is_valid_pos(grid, end):
            raise MazeError(f"End position {end} is outside the grid or on a wall.")

        self.grid = grid.astype(np.uint8)
        self.start = start
        self.end = end
        self.rows, self.cols = grid.shape

    # ── Constructors ──────────────────────────────────────────────

    @classmethod
    def from_image(cls, filepath: str) -> "Maze":
        """
        Create a Maze from a black-and-white PNG image.

        Args:
            filepath: Path to the image file.

        Returns:
            Maze instance.

        Raises:
            InvalidImageError: If the file cannot be read or is not a valid maze image.
            NoStartEndError: If start/end positions cannot be detected.
        """
        path = Path(filepath)
        if not path.exists():
            raise InvalidImageError(f"File not found: {filepath}")

        try:
            im = Image.open(filepath).convert("L")
        except Exception as e:
            raise InvalidImageError(f"Cannot open image: {e}")

        width, height = im.size
        if width < 3 or height < 3:
            raise InvalidImageError(
                f"Image too small ({width}x{height}). Minimum 3x3 required."
            )

        # Convert to binary numpy array: white(>128)=1, black(<=128)=0
        data = np.array(im)
        grid = (data > 128).astype(np.uint8)

        # Find start (first white pixel in top row)
        start = None
        for col in range(grid.shape[1]):
            if grid[0, col] == 1:
                start = (0, col)
                break

        if start is None:
            raise NoStartEndError("No open cell found in the top row (no start).")

        # Find end (first white pixel in last row)
        end = None
        for col in range(grid.shape[1]):
            if grid[grid.shape[0] - 1, col] == 1:
                end = (grid.shape[0] - 1, col)
                break

        if end is None:
            raise NoStartEndError("No open cell found in the bottom row (no end).")

        return cls(grid, start, end)

    @classmethod
    def from_grid(cls, grid: np.ndarray, start: tuple = None, end: tuple = None) -> "Maze":
        """
        Create a Maze from a pre-built numpy grid.

        If start/end not given, auto-detect from top/bottom rows.
        """
        if grid.ndim != 2:
            raise MazeError("Grid must be a 2D array.")

        if start is None:
            for col in range(grid.shape[1]):
                if grid[0, col] > 0:
                    start = (0, col)
                    break
            if start is None:
                raise NoStartEndError("No open cell in top row for start.")

        if end is None:
            for col in range(grid.shape[1]):
                if grid[grid.shape[0] - 1, col] > 0:
                    end = (grid.shape[0] - 1, col)
                    break
            if end is None:
                raise NoStartEndError("No open cell in bottom row for end.")

        return cls(grid, start, end)

    # ── Grid Queries ──────────────────────────────────────────────

    def is_valid(self, row: int, col: int) -> bool:
        """Check if position is within bounds and is a path cell."""
        return (0 <= row < self.rows and 0 <= col < self.cols
                and self.grid[row, col] == 1)

    def get_neighbors(self, row: int, col: int) -> list:
        """
        Get valid 4-directional neighbors of (row, col).

        Returns:
            List of (row, col) tuples for open neighbors.
        """
        neighbors = []
        for dr, dc in [(-1, 0), (0, 1), (1, 0), (0, -1)]:  # N, E, S, W
            nr, nc = row + dr, col + dc
            if self.is_valid(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    @property
    def total_cells(self) -> int:
        return self.rows * self.cols

    @property
    def open_cells(self) -> int:
        return int(np.sum(self.grid))

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _is_valid_pos(grid: np.ndarray, pos: tuple) -> bool:
        r, c = pos
        return (0 <= r < grid.shape[0] and 0 <= c < grid.shape[1]
                and grid[r, c] > 0)

    def __repr__(self) -> str:
        return (f"Maze(rows={self.rows}, cols={self.cols}, "
                f"start={self.start}, end={self.end}, "
                f"open_cells={self.open_cells})")
