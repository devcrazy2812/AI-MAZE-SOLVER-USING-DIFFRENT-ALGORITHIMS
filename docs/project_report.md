# Maze Solver AI — Project Report

## 1. Introduction

### 1.1 Problem Statement
Pathfinding is a fundamental problem in computer science and artificial intelligence. Given a maze represented as a grid of walls and open paths, the objective is to find a route from a designated start cell to an end cell. This project implements and visualizes three classical pathfinding algorithms—BFS, DFS, and A*—and provides a comparative analysis of their performance.

### 1.2 Objectives
1. Build a modular, scalable maze solver application in Python.
2. Implement BFS, DFS, and A* Search with real-time step-by-step animation.
3. Support maze loading from images and procedural maze generation.
4. Provide a performance comparison dashboard.
5. Create an interactive web-based UI using Streamlit.

### 1.3 Scope
- Unweighted 2D grid mazes with 4-directional movement.
- Black-and-white maze images (PNG/JPG).
- Procedurally generated perfect mazes using recursive backtracking.
- Manhattan and Euclidean heuristics for A*.

---

## 2. Literature Review

### 2.1 Breadth-First Search (BFS)
BFS was first described by Konrad Zuse in 1945 and independently by Edward F. Moore in 1959. It explores all neighbors at the current depth before moving to the next level, guaranteeing the shortest path in unweighted graphs. It uses a FIFO queue.

- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V)
- **Guarantee**: Shortest path (unweighted)

### 2.2 Depth-First Search (DFS)
DFS explores as far as possible along each branch before backtracking. While memory-efficient, it does not guarantee the shortest path. Uses a LIFO stack.

- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V) worst case
- **Guarantee**: None (finds *a* path, not necessarily the shortest)

### 2.3 A* Search
Introduced by Peter Hart, Nils Nilsson, and Bertram Raphael in 1968, A* uses a best-first search guided by f(n) = g(n) + h(n). It guarantees the optimal path when the heuristic is admissible (never overestimates).

- **Time Complexity**: O(E) with good heuristic, O(b^d) worst case
- **Space Complexity**: O(V)
- **Guarantee**: Optimal path (with admissible heuristic)

### 2.4 Maze Generation — Recursive Backtracking
A randomized DFS-based algorithm that carves passages through a grid of walls. Produces "perfect" mazes with exactly one path between any two cells.

---

## 3. System Design

### 3.1 Architecture

```
┌─────────────────────────────────────────┐
│              Streamlit UI               │
│  (sidebar controls, animation display)  │
├────────────┬────────────┬───────────────┤
│  algorithms │ visualization │   utils    │
│  bfs/dfs/a* │  renderer    │ image_proc │
│             │  charts      │ performance│
├─────────────┴────────────┴──────────────┤
│              core                        │
│      maze.py  •  maze_generator.py       │
├──────────────────────────────────────────┤
│         config.py (constants)            │
└──────────────────────────────────────────┘
```

### 3.2 Data Representation
- **Maze Grid**: Numpy 2D array (`np.uint8`), 0=wall, 1=path.
- **Advantages over linked-list nodes**: O(1) cell lookup, cache-friendly memory layout, direct matplotlib visualization, efficient neighbor computation.

### 3.3 Algorithm Animation
Each algorithm exposes a `solve_stepwise()` generator that yields a `SolveStep` dataclass at each iteration, containing the current cell, visited set, frontier set, and path so far. The UI iterates through these steps with a configurable delay.

### 3.4 Performance Measurement
- **Timing**: `time.perf_counter()` (high-resolution)
- **Memory**: `tracemalloc` (Python memory allocator tracking)
- Metrics: execution time (ms), nodes explored, peak memory (KB), path length

---

## 4. Implementation Details

### 4.1 Maze Loading from Image
1. Image opened with PIL, converted to grayscale.
2. Pixels binarized: value > 128 → path (1), else wall (0).
3. Start detected as first open cell in top row.
4. End detected as first open cell in bottom row.
5. Validation: file type, size (<5MB), dimensions (3×3 minimum, 1000×1000 maximum).

### 4.2 Maze Generation
- Iterative stack-based recursive backtracking (avoids Python's recursion limit).
- Grid forced to odd dimensions.
- Walls on even indices, passages on odd indices.
- Random neighbor selection creates unique mazes each run (optional seed for reproducibility).

### 4.3 Heuristic Functions
- **Manhattan**: `|Δrow| + |Δcol|` — optimal for 4-directional grids.
- **Euclidean**: `√(Δrow² + Δcol²)` — straight-line distance, less aggressive.

### 4.4 Frontend
Built with Streamlit, featuring:
- Sidebar with maze source selection, algorithm/heuristic dropdowns, animation speed slider.
- Real-time maze rendering using matplotlib with custom colormap.
- Performance comparison dashboard with grouped bar charts.

---

## 5. Results and Analysis

### 5.1 Expected Behavior
| Algorithm | Shortest Path? | Exploration Pattern | Speed |
|-----------|---------------|---------------------|-------|
| BFS | ✅ Yes | Level-by-level, broad | Moderate |
| DFS | ❌ No | Deep, can wander | Fast (finds *a* path) |
| A* Manhattan | ✅ Yes | Directed toward goal | Fast |
| A* Euclidean | ✅ Yes | Slightly broader than Manhattan | Moderate |

### 5.2 Key Observations
1. **BFS** always finds the shortest path but explores many unnecessary cells.
2. **DFS** finds paths quickly but they are often much longer than optimal.
3. **A* with Manhattan** typically explores the fewest nodes while guaranteeing optimality.
4. **A* with Euclidean** explores slightly more nodes than Manhattan because the heuristic is less tight for grid movement.

---

## 6. Conclusion
This project demonstrates a complete pipeline from maze input to interactive visualization of pathfinding algorithms. The modular architecture enables easy extension with new algorithms (e.g., Dijkstra, Greedy Best-First) or UI frameworks. The Streamlit frontend provides an accessible way for users to experimentally compare algorithm behavior and performance.

---

## 7. Future Work
- Add Dijkstra's algorithm and Greedy Best-First Search.
- Support diagonal movement (8-directional).
- Implement weighted mazes.
- Add maze export (save generated maze as PNG).
- Deploy as a web service (Streamlit Cloud).

---

## 8. References
1. Hart, P.E., Nilsson, N.J., Raphael, B. (1968). "A Formal Basis for the Heuristic Determination of Minimum Cost Paths." IEEE Transactions.
2. Cormen, T.H., et al. (2009). "Introduction to Algorithms," 3rd Edition. MIT Press.
3. LaValle, S.M. (2006). "Planning Algorithms." Cambridge University Press.
4. Streamlit Documentation: https://docs.streamlit.io
5. NumPy Documentation: https://numpy.org/doc
