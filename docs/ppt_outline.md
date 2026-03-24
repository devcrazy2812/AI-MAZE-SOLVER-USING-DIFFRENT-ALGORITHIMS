# Maze Solver AI — PPT Outline

> Suggested slide count: **18–22 slides**
> Duration: **15–20 minutes**

---

## Slide 1: Title Slide
- **Title**: Maze Solver AI — Interactive Pathfinding Visualization
- **Subtitle**: BFS • DFS • A* Search • Real-time Animation
- Team members, date, institution

---

## Slide 2: Agenda
1. Problem Statement
2. Objectives
3. Algorithms Overview
4. System Architecture
5. Data Representation
6. Maze Generation
7. Algorithm Animations (Demo)
8. A* Heuristics
9. Performance Comparison
10. Tech Stack
11. Demo
12. Future Work
13. Q&A

---

## Slide 3: Problem Statement
- Pathfinding in grids: fundamental AI problem
- Motivation: robotics, games, navigation, logistics
- Goal: compare algorithms visually and quantitatively

---

## Slide 4: Objectives
- Implement BFS, DFS, A* with visualization
- Real-time step-by-step animation
- Maze generation and image upload
- Performance benchmarking dashboard

---

## Slide 5: BFS — Breadth-First Search
- FIFO queue, level-by-level exploration
- Guarantees shortest path (unweighted)
- Time: O(V+E), Space: O(V)
- Diagram: expanding wavefront

---

## Slide 6: DFS — Depth-First Search
- LIFO stack, deep exploration
- Does NOT guarantee shortest path
- Time: O(V+E), Space: O(V)
- Diagram: deep branch exploration

---

## Slide 7: A* Search
- f(n) = g(n) + h(n)
- Priority queue (min-heap)
- Optimal with admissible heuristic
- Combines benefits of BFS + Greedy

---

## Slide 8: Heuristic Functions
- **Manhattan**: |Δrow| + |Δcol| — optimal for 4-directional
- **Euclidean**: √(Δrow² + Δcol²) — straight-line
- Visual comparison of exploration patterns

---

## Slide 9: System Architecture
- Diagram showing 5 modules: core, algorithms, visualization, ui, utils
- Data flow: Image → Grid → Algorithm → Animation → Dashboard

---

## Slide 10: Data Representation
- **Before**: Linked-list Node graph (O(n) lookup)
- **After**: Numpy 2D array (O(1) lookup)
- Memory and performance comparison

---

## Slide 11: Maze Generation
- Recursive Backtracking algorithm
- Iterative stack-based (avoids recursion limit)
- Produces perfect mazes
- Configurable size with random seed

---

## Slide 12: Image Upload & Validation
- Supported formats: PNG, JPG, BMP
- Validation: file type, size (≤5MB), dimensions
- Binary conversion: white=path, black=wall
- Auto-detect start (top row) and end (bottom row)

---

## Slide 13: Real-time Animation
- Generator-based `solve_stepwise()` function
- Yields: current cell, visited set, frontier set, partial path
- Color-coded: blue=visited, yellow=frontier, red=current, green=solution
- Configurable speed and step skipping

---

## Slide 14: Performance Dashboard
- Runs all algorithms on same maze
- Metrics: Time (ms), Nodes Explored, Memory (KB), Path Length
- Data table + grouped bar charts

---

## Slide 15: Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Visualization | Matplotlib |
| Grid | NumPy |
| Image I/O | Pillow (PIL) |
| Memory Profiling | tracemalloc |
| Language | Python 3.8+ |

---

## Slide 16: Live Demo
- Generate 21×21 maze
- Solve with BFS (show animation)
- Solve with A* Manhattan
- Run "Compare All" dashboard
- Upload custom maze image

---

## Slide 17: Results Summary
| Algorithm | Shortest? | Nodes (21×21) | Time |
|-----------|----------|---------------|------|
| BFS | ✅ | ~many | moderate |
| DFS | ❌ | ~fewer | fast |
| A* Manhattan | ✅ | ~fewest | fast |
| A* Euclidean | ✅ | ~some | moderate |

---

## Slide 18: Key Takeaways
1. BFS guarantees shortest but explores broadly
2. DFS is fast but path quality varies
3. A* is best balance of speed and optimality
4. Heuristic choice significantly impacts A* performance
5. Visualization makes algorithm behavior intuitive

---

## Slide 19: Future Work
- Add Dijkstra's, Greedy Best-First
- Diagonal movement support
- Weighted mazes
- Export / save mazes
- Cloud deployment

---

## Slide 20: Q&A
- Thank you!
- Questions?
