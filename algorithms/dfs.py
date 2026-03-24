"""
Depth-First Search (DFS) pathfinding algorithm.

Uses a LIFO stack for exploration. Does NOT guarantee the shortest path,
but is memory-efficient and explores deeply before backtracking.
"""

from collections import deque
from typing import Generator
import time
import tracemalloc

from .base import AlgorithmResult, SolveStep


def solve(maze) -> AlgorithmResult:
    """
    Solve the maze using DFS.

    Args:
        maze: A core.Maze instance.

    Returns:
        AlgorithmResult with path, visited order, and stats.
    """
    tracemalloc.start()
    t0 = time.perf_counter()

    start, end = maze.start, maze.end
    stack = [start]
    visited = set()
    visited_order = []
    prev = {start: None}
    found = False

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)
        visited_order.append(current)

        if current == end:
            found = True
            break

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                prev[neighbor] = current
                stack.append(neighbor)

    # Reconstruct path
    path = []
    if found:
        cell = end
        while cell is not None:
            path.append(cell)
            cell = prev.get(cell)
        path.reverse()

    t1 = time.perf_counter()
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return AlgorithmResult(
        path=path,
        visited_order=visited_order,
        found=found,
        stats={
            "nodes_explored": len(visited),
            "path_length": len(path),
            "time_ms": round((t1 - t0) * 1000, 3),
            "memory_kb": round(peak_memory / 1024, 2),
        },
    )


def solve_stepwise(maze) -> Generator[SolveStep, None, AlgorithmResult]:
    """
    Solve the maze using DFS, yielding each step for animation.

    Yields:
        SolveStep at each iteration.

    Returns:
        AlgorithmResult (accessible via generator.value after StopIteration).
    """
    start, end = maze.start, maze.end
    stack = [start]
    visited = set()
    visited_order = []
    prev = {start: None}
    found = False

    while stack:
        current = stack.pop()

        if current in visited:
            continue

        visited.add(current)
        visited_order.append(current)

        # Build path to current for visualization
        path_to_current = _reconstruct(prev, current)

        yield SolveStep(
            current=current,
            visited=set(visited),
            frontier=set(stack),
            path_so_far=path_to_current,
        )

        if current == end:
            found = True
            break

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                prev[neighbor] = current
                stack.append(neighbor)

    # Final path
    path = _reconstruct(prev, end) if found else []

    return AlgorithmResult(
        path=path,
        visited_order=visited_order,
        found=found,
        stats={"nodes_explored": len(visited), "path_length": len(path)},
    )


def _reconstruct(prev: dict, target: tuple) -> list:
    """Reconstruct path from prev map."""
    path = []
    cell = target
    while cell is not None:
        path.append(cell)
        cell = prev.get(cell)
    path.reverse()
    return path
