# 🧩 Maze Solver AI — Interactive Visualization Software

An interactive AI-powered maze solving and visualization tool built with Python and Streamlit. Supports **BFS**, **DFS**, and **A\* Search** with real-time algorithm animation, maze generation, image upload, and performance comparison dashboard.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Three Algorithms** | BFS, DFS, A* Search — all with step-by-step animation |
| 🎯 **Heuristic Selection** | Manhattan & Euclidean distance for A* |
| 🏗️ **Maze Generator** | Recursive backtracking algorithm, configurable size |
| 📤 **Image Upload** | Load maze from PNG/JPG image (black=wall, white=path) |
| 🎬 **Real-time Animation** | Visualize visited nodes, frontier, and final path |
| 📊 **Performance Dashboard** | Compare all algorithms: time, nodes, memory, path length |
| 🛡️ **Input Validation** | Safe file upload with type/size/dimension checks |
| 🧱 **Modular Architecture** | Clean separation: core, algorithms, visualization, ui, utils |

---

## 📁 Project Structure

```
MAZE SOLVER/
├── config.py                  # Global configuration constants
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── core/                      # Core maze logic
│   ├── __init__.py
│   ├── maze.py                # Numpy-based maze representation
│   └── maze_generator.py      # Recursive backtracking generator
│
├── algorithms/                # Pathfinding algorithms
│   ├── __init__.py
│   ├── base.py                # SolveStep & AlgorithmResult dataclasses
│   ├── bfs.py                 # Breadth-First Search
│   ├── dfs.py                 # Depth-First Search
│   └── astar.py               # A* Search (Manhattan / Euclidean)
│
├── visualization/             # Rendering & animation
│   ├── __init__.py
│   └── renderer.py            # Matplotlib maze renderer & chart builder
│
├── ui/                        # Streamlit frontend
│   ├── __init__.py
│   └── app.py                 # Main application entry point
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── image_processing.py    # Safe image upload & grid conversion
│   └── performance.py         # Timing & memory measurement
│
├── docs/                      # Documentation
│   ├── project_report.md      # Academic project report
│   ├── ppt_outline.md         # Presentation slide outline
│   └── viva_questions.md      # Viva voce Q&A
│
└── data/                      # Sample maze images
    ├── small.png
    └── small - Copy.png
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd "MAZE SOLVER"
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run ui/app.py
```

### 3. Use the App

1. **Generate a maze** using the sidebar controls (select size, click "Generate Maze")
   — OR **upload a maze image** (PNG/JPG, black=wall, white=path)
2. **Select an algorithm** (BFS, DFS, or A*)
3. For A*, **choose a heuristic** (Manhattan or Euclidean)
4. Click **"Solve & Animate"** to watch the algorithm explore the maze step-by-step
5. Click **"Compare All Algorithms"** to see a side-by-side performance dashboard

---

## 🧠 Algorithms

### BFS (Breadth-First Search)
- Explores level by level using a FIFO queue
- **Guarantees shortest path** in unweighted graphs
- Time: O(V + E) | Space: O(V)

### DFS (Depth-First Search)
- Explores as deep as possible using a LIFO stack
- **Does NOT guarantee shortest path**
- Time: O(V + E) | Space: O(V) (worst case)

### A* Search
- Uses f(n) = g(n) + h(n) with priority queue
- **Guarantees shortest path** with admissible heuristic
- Heuristics:
  - **Manhattan**: |Δrow| + |Δcol| — best for grid movement
  - **Euclidean**: √(Δrow² + Δcol²) — straight-line distance

---

## 🎨 Visualization Color Scheme

| Color | Meaning |
|-------|---------|
| ⬛ Black | Wall |
| ⬜ White | Open path |
| 🔵 Blue | Visited cells |
| 🟡 Yellow | Frontier (queued) |
| 🔴 Red | Current cell |
| 🟢 Green | Start / Solution path |
| 🔴 Red | End cell |

---

## 📊 Performance Dashboard

The comparison dashboard runs all algorithms on the same maze and displays:
- **Execution Time** (milliseconds)
- **Nodes Explored** (count)
- **Peak Memory Usage** (KB via tracemalloc)
- **Path Length** (steps)

Results are shown in both a data table and interactive bar charts.

---

## 🏗️ Maze Generator

Uses **recursive backtracking** (iterative, stack-based):
1. Start with a grid of walls
2. Carve passages by randomly choosing unvisited neighbors
3. Backtrack when no unvisited neighbors remain
4. Produces a **perfect maze** (exactly one path between any two cells)

---

## ⚙️ Configuration

Edit `config.py` to customize:
- `MAX_UPLOAD_SIZE_MB` — maximum upload file size
- `SUPPORTED_IMAGE_FORMATS` — allowed image extensions
- `DEFAULT_MAZE_ROWS` / `DEFAULT_MAZE_COLS` — default generation size
- `COLORS` — visualization color palette
- Animation speed defaults

---

## 📝 License

MIT License — free for academic and personal use.
