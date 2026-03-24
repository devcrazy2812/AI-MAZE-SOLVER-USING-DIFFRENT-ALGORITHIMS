# Maze Solver AI — Viva Voce Questions & Answers

## Algorithms

### Q1. What is BFS and how does it work?
**A:** BFS (Breadth-First Search) explores all nodes at the current depth level before moving to the next level. It uses a FIFO queue. Starting from the source, it visits all neighbors first, then neighbors of neighbors, etc. This guarantees the shortest path in unweighted graphs.

### Q2. What is DFS and how is it different from BFS?
**A:** DFS (Depth-First Search) explores as far as possible along each branch before backtracking. It uses a LIFO stack instead of a queue. Unlike BFS, DFS does NOT guarantee the shortest path — it finds *a* path, which may be longer than optimal.

### Q3. Explain A* Search algorithm.
**A:** A* uses a priority queue and evaluates nodes using f(n) = g(n) + h(n), where g(n) is the actual cost from start and h(n) is the heuristic estimate to the goal. It combines the completeness of BFS with the efficiency of greedy best-first search. With an admissible heuristic, A* guarantees the optimal path.

### Q4. What is an admissible heuristic?
**A:** An admissible heuristic never overestimates the actual cost to reach the goal. This property is essential for A* to guarantee finding the optimal (shortest) path. Both Manhattan and Euclidean distances are admissible for grid-based pathfinding.

### Q5. Compare Manhattan and Euclidean heuristics.
**A:** 
- **Manhattan** (|Δrow| + |Δcol|): Better for 4-directional grid movement because it matches the actual movement pattern. Results in fewer nodes explored.
- **Euclidean** (√(Δrow² + Δcol²)): Straight-line distance, always ≤ Manhattan. Being a looser bound, it causes A* to explore more nodes but is still admissible.

### Q6. What is the time complexity of BFS, DFS, and A*?
**A:**
- **BFS**: O(V + E) where V = vertices, E = edges
- **DFS**: O(V + E)
- **A***: Depends on heuristic quality. Best case O(E), worst case O(b^d) where b = branching factor, d = depth

### Q7. What is the space complexity of these algorithms?
**A:** All three are O(V) in the worst case. BFS stores all nodes at the current frontier level. DFS stores nodes along the current path (O(d) best case). A* stores all generated nodes in the open/closed sets.

### Q8. Why does DFS not guarantee the shortest path?
**A:** DFS always chooses to go deeper first, so it may reach the goal via a long, winding path instead of the direct route. It terminates as soon as it finds *any* path, not necessarily the shortest one.

### Q9. When would you prefer DFS over BFS?
**A:** When memory is limited (DFS uses less memory), when you only need to know if a path *exists* (not the shortest), or when solutions are deep in the search tree and you want to find them quickly.

---

## Data Structures

### Q10. Why did you use numpy arrays instead of linked-list nodes?
**A:** Numpy arrays provide O(1) random access to any cell, contiguous memory layout (cache-friendly), efficient bulk operations, and direct compatibility with matplotlib for visualization. Linked-list nodes have O(n) traversal, more memory overhead per node, and are harder to visualize.

### Q11. What data structure does BFS use? Why?
**A:** A FIFO queue (Python's `collections.deque`). The queue ensures nodes are processed in the order they were discovered, which guarantees level-by-level exploration and shortest path in unweighted graphs.

### Q12. What data structure does A* use? Why?
**A:** A priority queue (min-heap via Python's `heapq`). This ensures the node with the lowest f(n) = g(n) + h(n) is always processed next, directing the search toward the most promising path.

### Q13. What is a Fibonacci heap and why was it in the original code?
**A:** A Fibonacci heap is an advanced priority queue with O(1) amortized insert and decrease-key operations (vs O(log n) for binary heaps). The original code used it for Dijkstra/A*. In our refactored version, we use Python's `heapq` (binary heap) because it's simpler and sufficient for the maze sizes we handle.

---

## Design & Architecture

### Q14. Explain the modular architecture of your project.
**A:**
- **core/**: Maze data structure and maze generator
- **algorithms/**: BFS, DFS, A* — all with consistent interfaces
- **visualization/**: Matplotlib-based rendering
- **ui/**: Streamlit frontend
- **utils/**: Image processing, performance measurement
- **config.py**: Central configuration

This separation follows the Single Responsibility Principle and makes components independently testable and reusable.

### Q15. What design pattern does the algorithm selector use?
**A:** The Strategy Pattern. Each algorithm implements the same interface (`solve(maze)` and `solve_stepwise(maze)`), and the UI selects which strategy to use at runtime based on user input.

### Q16. How does the animation system work?
**A:** Each algorithm has a `solve_stepwise()` function implemented as a Python generator. It yields a `SolveStep` object at each iteration containing the current cell, visited set, frontier set, and partial path. The UI iterates through these steps, renders each one, and adds a time delay for animation.

### Q17. What is a generator in Python? Why use it here?
**A:** A generator is a function that uses `yield` to produce values lazily, one at a time. We use it because generating all animation frames upfront would consume too much memory. With generators, we produce and display one frame at a time, enabling smooth real-time animation.

---

## Maze Generation

### Q18. Explain the recursive backtracking algorithm.
**A:**
1. Start with a grid full of walls.
2. Choose a starting cell, mark it as a passage.
3. Randomly select an unvisited neighbor (2 cells away).
4. Carve through the wall between current and chosen cell.
5. Move to the chosen cell and repeat.
6. If no unvisited neighbors, backtrack to the previous cell.
7. Continue until all cells are visited.

### Q19. Why use iterative stack instead of actual recursion?
**A:** Python has a default recursion limit of ~1000. For large mazes (e.g., 101×101 = ~2500 carving cells), recursive calls would hit this limit. The iterative stack version has no such limitation and is more memory-efficient.

### Q20. What is a "perfect maze"?
**A:** A perfect maze has exactly one path between any two cells. There are no loops and no inaccessible areas. This is what recursive backtracking generates.

---

## Image Processing

### Q21. How do you convert an image to a maze?
**A:**
1. Open the image and convert to grayscale using PIL.
2. Convert to a numpy array.
3. Binarize: pixels > 128 become 1 (path), ≤ 128 become 0 (wall).
4. Detect start (first white pixel in top row) and end (first white pixel in bottom row).

### Q22. What input validation do you perform?
**A:**
- File extension check (PNG, JPG, JPEG, BMP only)
- File size limit (≤ 5 MB)
- Image dimension check (min 3×3, max 1000×1000)
- Start/end existence verification
- Grid validity (must be 2D binary array)

### Q23. How do you handle invalid inputs?
**A:** Custom exception hierarchy: `MazeError` (base) → `InvalidImageError`, `NoStartEndError`. The `utils/image_processing.py` module raises `InvalidImageError` and `ImageTooLargeError`. The UI catches these and displays user-friendly error messages via `st.error()`.

---

## Performance & Measurement

### Q24. How do you measure execution time?
**A:** Using `time.perf_counter()`, which provides the highest resolution timer available on the system. We measure before and after the solve function call.

### Q25. How do you measure memory usage?
**A:** Using Python's `tracemalloc` module, which traces memory allocations. We call `tracemalloc.start()` before and `tracemalloc.get_traced_memory()` after to get peak memory usage in bytes.

### Q26. Why compare algorithms on the same maze?
**A:** To ensure a fair comparison. Different mazes have different characteristics (complexity, path length, branching factor). By using the same maze, we isolate the algorithm's behavior as the only variable.

---

## Technical Details

### Q27. What is Streamlit and why did you choose it?
**A:** Streamlit is a Python framework for building interactive web applications with minimal code. We chose it over Pygame (not web-deployable) and React+Flask (too complex) because it provides built-in widgets, easy matplotlib integration, and rapid prototyping — perfect for a visualization tool.

### Q28. How does `st.empty()` enable animation?
**A:** `st.empty()` creates a placeholder container in the Streamlit layout. We can call `.pyplot()` on it repeatedly to replace its content — each call renders a new animation frame in place, creating the illusion of animation without appending new elements.

### Q29. What is the purpose of `config.py`?
**A:** Centralized configuration prevents magic numbers scattered across the codebase. It defines upload constraints, default values, color schemes, and animation parameters. Changing a constant in one place updates behavior everywhere.

### Q30. How would you add a new algorithm (e.g., Dijkstra)?
**A:**
1. Create `algorithms/dijkstra.py` with `solve()` and `solve_stepwise()` functions.
2. Add it to `algorithms/__init__.py`.
3. Add an entry in `config.py`'s `ALGORITHMS` dict.
4. The UI automatically picks it up from the dropdown — no other changes needed.

---

## Advanced Questions

### Q31. What is the difference between A* and Dijkstra's algorithm?
**A:** Dijkstra uses f(n) = g(n) only (no heuristic), exploring in all directions equally. A* adds h(n) to guide the search toward the goal, typically exploring far fewer nodes. On unweighted grids, BFS is equivalent to Dijkstra.

### Q32. Can A* with Euclidean heuristic give a sub-optimal path?
**A:** No. Euclidean distance is admissible (never overestimates) for both 4-directional and 8-directional movement. It guarantees optimality. However, because it's a looser bound than Manhattan for 4-directional grids, it may explore more nodes.

### Q33. What happens if the heuristic overestimates?
**A:** The algorithm becomes inadmissible and may not find the optimal path. It could still find *a* path, but there's no guarantee it will be the shortest. The search may skip better paths because it incorrectly prioritizes nodes that appear closer.

### Q34. How would you handle weighted mazes?
**A:** Modify `maze.get_neighbors()` to return `(neighbor, weight)` tuples. Update algorithm `g_score` calculations to use actual weights instead of uniform cost. BFS would need to be replaced by Dijkstra for weighted graphs.

### Q35. What is the significance of the "frontier" in the visualization?
**A:** The frontier represents nodes that have been discovered but not yet processed. It shows the "boundary" of the search. For BFS, the frontier is a ring. For DFS, it's a narrow line. For A*, it's concentrated toward the goal. This visual difference helps understand each algorithm's exploration strategy.
