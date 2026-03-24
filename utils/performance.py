"""
Performance measurement utilities.

Wraps algorithm execution with timing (perf_counter) and memory
tracking (tracemalloc) for fair comparison.
"""

import time
import tracemalloc
from typing import Dict

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def measure_performance(solve_func, maze, **kwargs) -> dict:
    """
    Run an algorithm and measure its performance.

    Args:
        solve_func: Algorithm solve function (from algorithms module).
        maze: core.Maze instance.
        **kwargs: Extra arguments passed to solve_func (e.g. heuristic).

    Returns:
        dict with keys: "result" (AlgorithmResult), "time_ms", "memory_kb",
        "nodes_explored", "path_length", "found".
    """
    # Start memory tracking
    tracemalloc.start()

    t0 = time.perf_counter()
    result = solve_func(maze, **kwargs)
    t1 = time.perf_counter()

    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_ms = round((t1 - t0) * 1000, 3)
    memory_kb = round(peak_memory / 1024, 2)

    # Override stats with our more accurate measurements
    result.stats["time_ms"] = elapsed_ms
    result.stats["memory_kb"] = memory_kb

    return {
        "result": result,
        "time_ms": elapsed_ms,
        "memory_kb": memory_kb,
        "nodes_explored": result.stats.get("nodes_explored", 0),
        "path_length": result.stats.get("path_length", 0),
        "found": result.found,
    }


def compare_algorithms(maze, algorithms: dict) -> Dict[str, dict]:
    """
    Run multiple algorithms on the same maze and compare performance.

    Args:
        maze: core.Maze instance.
        algorithms: dict mapping display_name → (solve_func, kwargs_dict).
            Example: {"BFS": (bfs.solve, {}), "A* Manhattan": (astar.solve, {"heuristic": "manhattan"})}

    Returns:
        dict mapping display_name → performance dict (from measure_performance).
    """
    results = {}
    for name, (solve_func, kwargs) in algorithms.items():
        results[name] = measure_performance(solve_func, maze, **kwargs)
    return results
