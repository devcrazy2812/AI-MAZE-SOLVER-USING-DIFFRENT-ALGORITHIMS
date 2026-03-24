"""
Base data structures for algorithm results and animation steps.
"""

from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional


@dataclass
class SolveStep:
    """
    A single step of the algorithm, yielded for animation.

    Attributes:
        current: The cell currently being processed.
        visited: Set of all visited cells so far.
        frontier: Set of cells currently in the frontier (queue/stack/heap).
        path_so_far: Partial path from start to current (for A*, shows best-known path).
    """
    current: Tuple[int, int]
    visited: Set[Tuple[int, int]]
    frontier: Set[Tuple[int, int]]
    path_so_far: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class AlgorithmResult:
    """
    Complete result from running a pathfinding algorithm.

    Attributes:
        path: List of (row, col) from start to end. Empty if no path.
        visited_order: Cells in the order they were visited.
        found: Whether a path was found.
        stats: Performance statistics.
    """
    path: List[Tuple[int, int]]
    visited_order: List[Tuple[int, int]]
    found: bool
    stats: dict = field(default_factory=dict)
    # stats keys: "nodes_explored", "path_length", "time_ms", "memory_kb"
