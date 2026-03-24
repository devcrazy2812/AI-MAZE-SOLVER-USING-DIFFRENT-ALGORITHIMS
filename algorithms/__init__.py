"""Pathfinding algorithms module."""
from .bfs import solve as solve_bfs, solve_stepwise as solve_bfs_stepwise
from .dfs import solve as solve_dfs, solve_stepwise as solve_dfs_stepwise
from .astar import solve as solve_astar, solve_stepwise as solve_astar_stepwise
from .base import AlgorithmResult, SolveStep

__all__ = [
    "solve_bfs", "solve_bfs_stepwise",
    "solve_dfs", "solve_dfs_stepwise",
    "solve_astar", "solve_astar_stepwise",
    "AlgorithmResult", "SolveStep",
]
