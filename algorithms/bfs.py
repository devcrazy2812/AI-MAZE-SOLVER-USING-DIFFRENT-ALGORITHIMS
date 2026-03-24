"""
Breadth-First Search (BFS) pathfinding algorithm.

Uses a FIFO queue to explore all cells at distance d before exploring
cells at distance d+1, guaranteeing the shortest path in unweighted graphs.
"""

from collections import deque
from typing import Generator
import time
import tracemalloc

from .base import AlgorithmResult, SolveStep


def solve(maze) -> AlgorithmResult:
    """
    Solve the maze using BFS.

    Args:
        maze: A core.Maze instance.

    Returns:
        AlgorithmResult with path, visited order, and stats.
    """
    tracemalloc.start()
    t0 = time.perf_counter()

    start, end = maze.start, maze.end
    queue = deque([start])
    visited = {start}
    visited_order = [start]
    prev = {start: None}
    found = False

    while queue:
        current = queue.popleft()

        if current == end:
            found = True
            break

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                visited_order.append(neighbor)
                prev[neighbor] = current
                queue.append(neighbor)

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
    Solve the maze using BFS, yielding each step for animation.

    Yields:
        SolveStep at each iteration.

    Returns:
        AlgorithmResult (accessible via generator.value after StopIteration).
    """
    start, end = maze.start, maze.end
    queue = deque([start])
    visited = {start}
    visited_order = [start]
    prev = {start: None}
    found = False

    while queue:
        current = queue.popleft()

        # Build path to current for visualization
        path_to_current = _reconstruct(prev, current)

        yield SolveStep(
            current=current,
            visited=set(visited),
            frontier=set(queue),
            path_so_far=path_to_current,
        )

        if current == end:
            found = True
            break

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                visited_order.append(neighbor)
                prev[neighbor] = current
                queue.append(neighbor)

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
