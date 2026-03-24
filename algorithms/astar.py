"""
A* Search pathfinding algorithm.

Uses a priority queue with f(n) = g(n) + h(n) where:
  g(n) = cost from start to n
  h(n) = heuristic estimate from n to end
Guarantees shortest path when heuristic is admissible.
"""

import heapq
import math
import time
import tracemalloc
from typing import Generator

from .base import AlgorithmResult, SolveStep


# ── Heuristic Functions ──────────────────────────────────────────

def manhattan(a: tuple, b: tuple) -> float:
    """Manhattan (taxicab) distance: |Δrow| + |Δcol|."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a: tuple, b: tuple) -> float:
    """Euclidean (straight-line) distance: √(Δrow² + Δcol²)."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


HEURISTICS = {
    "manhattan": manhattan,
    "euclidean": euclidean,
}


def _get_heuristic(name: str):
    """Get heuristic function by name."""
    h = HEURISTICS.get(name.lower())
    if h is None:
        raise ValueError(
            f"Unknown heuristic '{name}'. Choose from: {list(HEURISTICS.keys())}"
        )
    return h


# ── Full Solve ────────────────────────────────────────────────────

def solve(maze, heuristic: str = "manhattan") -> AlgorithmResult:
    """
    Solve the maze using A* search.

    Args:
        maze: A core.Maze instance.
        heuristic: "manhattan" or "euclidean".

    Returns:
        AlgorithmResult with path, visited order, and stats.
    """
    h = _get_heuristic(heuristic)

    tracemalloc.start()
    t0 = time.perf_counter()

    start, end = maze.start, maze.end

    # Priority queue entries: (f_cost, counter, cell)
    # counter breaks ties to avoid comparing tuples of cells
    counter = 0
    open_set = [(h(start, end), counter, start)]
    g_score = {start: 0}
    prev = {start: None}
    closed_set = set()
    visited_order = []

    found = False

    while open_set:
        f, _, current = heapq.heappop(open_set)

        if current in closed_set:
            continue

        closed_set.add(current)
        visited_order.append(current)

        if current == end:
            found = True
            break

        for neighbor in maze.get_neighbors(*current):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + 1  # uniform cost = 1 per step

            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                f_score = tentative_g + h(neighbor, end)
                prev[neighbor] = current
                counter += 1
                heapq.heappush(open_set, (f_score, counter, neighbor))

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
            "nodes_explored": len(closed_set),
            "path_length": len(path),
            "time_ms": round((t1 - t0) * 1000, 3),
            "memory_kb": round(peak_memory / 1024, 2),
            "heuristic": heuristic,
        },
    )


# ── Step-wise Solve (for animation) ──────────────────────────────

def solve_stepwise(
    maze, heuristic: str = "manhattan"
) -> Generator[SolveStep, None, AlgorithmResult]:
    """
    Solve the maze using A*, yielding each step for animation.

    Yields:
        SolveStep at each iteration.
    """
    h = _get_heuristic(heuristic)

    start, end = maze.start, maze.end

    counter = 0
    open_set = [(h(start, end), counter, start)]
    g_score = {start: 0}
    prev = {start: None}
    closed_set = set()
    visited_order = []

    found = False

    while open_set:
        f, _, current = heapq.heappop(open_set)

        if current in closed_set:
            continue

        closed_set.add(current)
        visited_order.append(current)

        # Frontier cells for visualization
        frontier_cells = {entry[2] for entry in open_set if entry[2] not in closed_set}

        path_to_current = _reconstruct(prev, current)

        yield SolveStep(
            current=current,
            visited=set(closed_set),
            frontier=frontier_cells,
            path_so_far=path_to_current,
        )

        if current == end:
            found = True
            break

        for neighbor in maze.get_neighbors(*current):
            if neighbor in closed_set:
                continue

            tentative_g = g_score[current] + 1

            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                f_score = tentative_g + h(neighbor, end)
                prev[neighbor] = current
                counter += 1
                heapq.heappush(open_set, (f_score, counter, neighbor))

    # Final path
    path = _reconstruct(prev, end) if found else []

    return AlgorithmResult(
        path=path,
        visited_order=visited_order,
        found=found,
        stats={
            "nodes_explored": len(closed_set),
            "path_length": len(path),
            "heuristic": heuristic,
        },
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
