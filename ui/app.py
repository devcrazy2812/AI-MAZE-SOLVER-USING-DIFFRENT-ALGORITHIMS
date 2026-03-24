"""
Maze Solver AI - Interactive Visualization Software
=====================================================
Premium Streamlit-based frontend with real-time algorithm animation,
maze generation, image upload, and performance comparison dashboard.

Run with:
    python -m streamlit run ui/app.py
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import os

# ── Path setup ────────────────────────────────────────────────────
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.maze import Maze, MazeError, NoStartEndError
from core.maze_generator import generate_maze
from algorithms import bfs, dfs, astar
from algorithms.base import AlgorithmResult
from visualization.renderer import (
    render_maze, render_step, render_solution, render_comparison_chart,
)
from utils.image_processing import validate_upload, process_image
from utils.image_processing import InvalidImageError as UploadError
from utils.performance import compare_algorithms
from config import (
    ALGORITHMS, HEURISTICS,
    DEFAULT_MAZE_ROWS, DEFAULT_MAZE_COLS,
    DEFAULT_ANIMATION_SPEED_MS, MIN_ANIMATION_SPEED_MS, MAX_ANIMATION_SPEED_MS,
)

# ═══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Maze Solver AI - Pathfinding Visualizer",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
#  PREMIUM CSS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── Import Google Fonts ────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ── Root & Theme ───────────────────────────────────────── */
    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: rgba(17, 24, 39, 0.7);
        --bg-card-hover: rgba(30, 41, 59, 0.8);
        --border-subtle: rgba(99, 102, 241, 0.15);
        --border-glow: rgba(99, 102, 241, 0.4);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-purple: #8b5cf6;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-rose: #f43f5e;
        --accent-amber: #f59e0b;
        --gradient-main: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-card: linear-gradient(145deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.05) 100%);
        --shadow-glow: 0 0 30px rgba(99, 102, 241, 0.15);
    }

    /* ── Global ─────────────────────────────────────────────── */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* ── Sidebar ────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1629 0%, #0d1321 50%, #111827 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.02em;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: var(--accent-purple) !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: var(--border-subtle) !important;
        margin: 1rem 0 !important;
    }
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stNumberInput label,
    section[data-testid="stSidebar"] .stRadio label {
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
    }

    /* ── Header ─────────────────────────────────────────────── */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1rem;
        position: relative;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 3rem;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 40%, #f472b6 70%, #fb923c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.2;
        position: relative;
        z-index: 1;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        color: var(--text-muted);
        font-size: 1rem;
        font-weight: 400;
        margin-top: 0.5rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        position: relative;
        z-index: 1;
    }
    .hero-divider {
        width: 80px;
        height: 3px;
        background: var(--gradient-main);
        margin: 1.2rem auto 0;
        border-radius: 2px;
        position: relative;
        z-index: 1;
    }

    /* ── Legend ──────────────────────────────────────────────── */
    .legend-container {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        flex-wrap: wrap;
        padding: 0.75rem 1.5rem;
        background: var(--gradient-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        margin: 1rem auto;
        max-width: 800px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        font-weight: 500;
        color: var(--text-secondary);
        letter-spacing: 0.02em;
    }
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 3px;
        display: inline-block;
        box-shadow: 0 0 6px rgba(255,255,255,0.1);
    }

    /* ── Metric Cards ───────────────────────────────────────── */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    @media (max-width: 768px) {
        .metrics-grid { grid-template-columns: repeat(2, 1fr); }
    }
    .metric-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 1.25rem 1rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: var(--gradient-main);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .metric-card:hover {
        border-color: var(--border-glow);
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }
    .metric-card:hover::before { opacity: 1; }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 1.6rem;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.3;
    }
    .metric-value.purple { color: var(--accent-purple); }
    .metric-value.blue { color: var(--accent-blue); }
    .metric-value.cyan { color: var(--accent-cyan); }
    .metric-value.emerald { color: var(--accent-emerald); }
    .metric-value.rose { color: var(--accent-rose); }
    .metric-value.amber { color: var(--accent-amber); }
    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.4rem;
    }
    .metric-icon {
        font-size: 1.2rem;
        margin-bottom: 0.3rem;
        display: block;
    }

    /* ── Section Headers ────────────────────────────────────── */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.25rem;
        color: var(--text-primary);
        margin: 1.5rem 0 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-header .icon {
        font-size: 1.3rem;
    }
    .section-header .accent {
        color: var(--accent-purple);
    }

    /* ── Algo Badge ─────────────────────────────────────────── */
    .algo-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 1rem;
        background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1));
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 30px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        font-weight: 600;
        color: #a5b4fc;
        letter-spacing: 0.03em;
    }

    /* ── Footer ─────────────────────────────────────────────── */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        border-top: 1px solid var(--border-subtle);
        margin-top: 2rem;
    }
    .footer p {
        font-family: 'Inter', sans-serif;
        color: var(--text-muted);
        font-size: 0.8rem;
        font-weight: 400;
        letter-spacing: 0.03em;
    }
    .footer .brand {
        color: var(--accent-purple);
        font-weight: 600;
    }

    /* ── Streamlit overrides ────────────────────────────────── */
    .stButton > button[kind="primary"] {
        background: var(--gradient-main) !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(99,102,241,0.25) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(99,102,241,0.4) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="secondary"],
    .stButton > button:not([kind="primary"]) {
        background: transparent !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.3s !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: var(--accent-purple) !important;
        color: var(--accent-purple) !important;
        background: rgba(99,102,241,0.05) !important;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: var(--gradient-main) !important;
    }

    /* Data table */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 0.5rem 0 0.75rem;">
        <span style="font-size:2rem;">🧩</span>
        <div style="font-family:'Inter',sans-serif; font-weight:800; font-size:1.15rem; 
            color:#f1f5f9; margin-top:0.2rem; letter-spacing:-0.01em;">
            Maze Solver AI
        </div>
        <div style="font-family:'Inter',sans-serif; font-size:0.7rem; color:#64748b; 
            text-transform:uppercase; letter-spacing:0.12em; margin-top:0.15rem;">
            Pathfinding Visualizer
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Maze Source ────────────────────────────────────────────
    st.markdown("### Maze Source")
    source = st.radio(
        "Choose source:", ["Generate Maze", "Upload Image"],
        horizontal=True, label_visibility="collapsed"
    )

    if source == "Generate Maze":
        maze_rows = st.slider("Rows", min_value=5, max_value=101,
                              value=DEFAULT_MAZE_ROWS, step=2,
                              help="Odd numbers only for proper maze structure")
        maze_cols = st.slider("Columns", min_value=5, max_value=101,
                              value=DEFAULT_MAZE_COLS, step=2,
                              help="Odd numbers only for proper maze structure")
        seed = st.number_input("Random Seed (0 = random)", min_value=0,
                               max_value=99999, value=0, step=1)
        gen_btn = st.button("Generate Maze", use_container_width=True,
                            type="primary", icon="🔄")
    else:
        uploaded_file = st.file_uploader(
            "Upload maze image",
            type=["png", "jpg", "jpeg", "bmp"],
            help="Black & white image: White = path, Black = wall. "
                 "Top row = start opening, Bottom row = end opening."
        )

    st.markdown("---")

    # ── Algorithm ─────────────────────────────────────────────
    st.markdown("### Algorithm")
    algo_display = st.selectbox("Select algorithm", list(ALGORITHMS.keys()),
                                label_visibility="collapsed")
    algo_key = ALGORITHMS[algo_display]

    heuristic_key = "manhattan"
    if algo_key == "astar":
        st.markdown(
            '<p style="font-size:0.75rem; color:#64748b; margin:-0.5rem 0 0.3rem; '
            'text-transform:uppercase; letter-spacing:0.08em; font-weight:500;">'
            'Heuristic Function</p>',
            unsafe_allow_html=True
        )
        h_display = st.selectbox("Heuristic", list(HEURISTICS.keys()),
                                 label_visibility="collapsed")
        heuristic_key = HEURISTICS[h_display]

    st.markdown("---")

    # ── Animation Controls ────────────────────────────────────
    st.markdown("### Animation")
    anim_speed = st.slider(
        "Speed (ms/step)", min_value=MIN_ANIMATION_SPEED_MS,
        max_value=MAX_ANIMATION_SPEED_MS, value=DEFAULT_ANIMATION_SPEED_MS,
        step=10,
    )
    skip_steps = st.slider(
        "Show every Nth step", min_value=1, max_value=20, value=1,
        help="Skip steps for faster animation on large mazes"
    )

    st.markdown("---")

    # ── Action Buttons ────────────────────────────────────────
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        solve_btn = st.button("Solve", use_container_width=True,
                              type="primary", icon="▶️")
    with col_btn2:
        compare_btn = st.button("Compare", use_container_width=True,
                                icon="📊")

    st.markdown(
        '<p style="text-align:center; font-size:0.7rem; color:#475569; margin-top:0.5rem;">'
        'Solve = animate selected algo<br>Compare = benchmark all algos</p>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════════
#  MAIN AREA — HEADER
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">Maze Solver AI</h1>
    <p class="hero-subtitle">Interactive Pathfinding Visualization</p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)

# ── Color Legend ──────────────────────────────────────────────
st.markdown("""
<div class="legend-container">
    <span class="legend-item"><span class="legend-dot" style="background:#1e1e26"></span>Wall</span>
    <span class="legend-item"><span class="legend-dot" style="background:#f8fafc"></span>Path</span>
    <span class="legend-item"><span class="legend-dot" style="background:#5a8de6"></span>Visited</span>
    <span class="legend-item"><span class="legend-dot" style="background:#fbbf24"></span>Frontier</span>
    <span class="legend-item"><span class="legend-dot" style="background:#ef4444"></span>Current</span>
    <span class="legend-item"><span class="legend-dot" style="background:#22c55e"></span>Start</span>
    <span class="legend-item"><span class="legend-dot" style="background:#ef4444; opacity:0.8"></span>End</span>
    <span class="legend-item"><span class="legend-dot" style="background:linear-gradient(135deg,#22c55e,#10b981)"></span>Solution</span>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

if "maze" not in st.session_state:
    st.session_state.maze = None

# ── Generate / Upload Maze ────────────────────────────────────
if source == "Generate Maze":
    if gen_btn:
        with st.spinner("Generating maze..."):
            try:
                s = seed if seed > 0 else None
                grid = generate_maze(maze_rows, maze_cols, seed=s)
                st.session_state.maze = Maze.from_grid(grid)
                st.toast(f"Maze generated: {maze_rows} x {maze_cols}", icon="✅")
            except Exception as e:
                st.error(f"Generation failed: {e}")
else:
    if uploaded_file is not None:
        try:
            grid = process_image(uploaded_file)
            st.session_state.maze = Maze.from_grid(grid)
            st.toast(f"Image loaded: {grid.shape[0]} x {grid.shape[1]}", icon="✅")
        except (UploadError, MazeError) as e:
            st.error(f"{e}")

maze_obj = st.session_state.maze

if maze_obj is None:
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; margin:2rem auto; max-width:500px;">
        <div style="font-size:4rem; margin-bottom:1rem; opacity:0.6;">🏗️</div>
        <h3 style="font-family:'Inter',sans-serif; color:#e2e8f0; font-weight:600; margin:0 0 0.5rem;">
            No Maze Loaded
        </h3>
        <p style="font-family:'Inter',sans-serif; color:#64748b; font-size:0.9rem; line-height:1.6;">
            Generate a maze or upload an image from the sidebar to begin visualizing pathfinding algorithms.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════════════════════════════
#  MAZE INFO CARDS
# ═══════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="metrics-grid">
    <div class="metric-card">
        <span class="metric-icon">📐</span>
        <div class="metric-value purple">{maze_obj.rows} x {maze_obj.cols}</div>
        <div class="metric-label">Dimensions</div>
    </div>
    <div class="metric-card">
        <span class="metric-icon">🔲</span>
        <div class="metric-value cyan">{maze_obj.open_cells}</div>
        <div class="metric-label">Open Cells</div>
    </div>
    <div class="metric-card">
        <span class="metric-icon">🟢</span>
        <div class="metric-value emerald">{maze_obj.start}</div>
        <div class="metric-label">Start</div>
    </div>
    <div class="metric-card">
        <span class="metric-icon">🔴</span>
        <div class="metric-value rose">{maze_obj.end}</div>
        <div class="metric-label">End</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  SOLVE & ANIMATE
# ═══════════════════════════════════════════════════════════════════

if solve_btn:
    st.markdown(f"""
    <div class="section-header">
        <span class="icon">🔍</span>
        Solving with <span class="algo-badge">{algo_display}</span>
    </div>
    """, unsafe_allow_html=True)

    # Select solver
    if algo_key == "bfs":
        stepper = bfs.solve_stepwise(maze_obj)
        full_solver = bfs.solve
    elif algo_key == "dfs":
        stepper = dfs.solve_stepwise(maze_obj)
        full_solver = dfs.solve
    else:
        stepper = astar.solve_stepwise(maze_obj, heuristic=heuristic_key)
        full_solver = astar.solve

    # Animation containers
    viz_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_placeholder = st.empty()

    total_open = maze_obj.open_cells
    step_count = 0

    try:
        for step in stepper:
            step_count += 1

            if step_count % skip_steps == 0:
                fig = render_step(
                    maze_obj.grid, step,
                    start=maze_obj.start, end=maze_obj.end,
                )
                viz_placeholder.pyplot(fig, use_container_width=True)
                plt.close(fig)

                progress = min(1.0, len(step.visited) / total_open)
                progress_bar.progress(progress)
                status_placeholder.caption(
                    f"Step {step_count}  ·  Visited: {len(step.visited)}  "
                    f"·  Frontier: {len(step.frontier)}"
                )
                time.sleep(anim_speed / 1000.0)
    except StopIteration:
        pass

    progress_bar.progress(1.0)

    # Full solve for accurate stats
    if algo_key == "astar":
        result = astar.solve(maze_obj, heuristic=heuristic_key)
    else:
        result = full_solver(maze_obj)

    # Show solution
    if result.found:
        fig_sol = render_solution(
            maze_obj.grid, result.path,
            start=maze_obj.start, end=maze_obj.end,
        )
        viz_placeholder.pyplot(fig_sol, use_container_width=True)
        plt.close(fig_sol)

        status_placeholder.success(
            f"Path found!  ·  Length: {result.stats['path_length']}  ·  "
            f"Nodes explored: {result.stats['nodes_explored']}  ·  "
            f"Time: {result.stats['time_ms']:.2f} ms  ·  "
            f"Memory: {result.stats['memory_kb']:.1f} KB"
        )

        # Performance cards
        st.markdown("""
        <div class="section-header">
            <span class="icon">📈</span>
            Performance <span class="accent">Metrics</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <span class="metric-icon">⚡</span>
                <div class="metric-value blue">{result.stats["time_ms"]:.2f} ms</div>
                <div class="metric-label">Execution Time</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">🔎</span>
                <div class="metric-value purple">{result.stats["nodes_explored"]}</div>
                <div class="metric-label">Nodes Explored</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">💾</span>
                <div class="metric-value cyan">{result.stats["memory_kb"]:.1f} KB</div>
                <div class="metric-label">Peak Memory</div>
            </div>
            <div class="metric-card">
                <span class="metric-icon">📏</span>
                <div class="metric-value emerald">{result.stats["path_length"]}</div>
                <div class="metric-label">Path Length</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        status_placeholder.error("No path found in this maze.")

elif not compare_btn:
    # Show base maze when no action
    fig = render_maze(maze_obj.grid, start=maze_obj.start, end=maze_obj.end)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════
#  COMPARE ALL ALGORITHMS
# ═══════════════════════════════════════════════════════════════════

if compare_btn:
    st.markdown("""
    <div class="section-header">
        <span class="icon">📊</span>
        Algorithm <span class="accent">Comparison Dashboard</span>
    </div>
    """, unsafe_allow_html=True)

    algo_map = {
        "BFS": (bfs.solve, {}),
        "DFS": (dfs.solve, {}),
        "A* (Manhattan)": (astar.solve, {"heuristic": "manhattan"}),
        "A* (Euclidean)": (astar.solve, {"heuristic": "euclidean"}),
    }

    with st.spinner("Benchmarking all algorithms..."):
        comp_results = compare_algorithms(maze_obj, algo_map)

    # Results table
    table_data = []
    result_objects = {}
    for name, perf in comp_results.items():
        table_data.append({
            "Algorithm": name,
            "Time (ms)": perf["time_ms"],
            "Nodes Explored": perf["nodes_explored"],
            "Path Length": perf["path_length"],
            "Memory (KB)": perf["memory_kb"],
            "Found": "Yes" if perf["found"] else "No",
        })
        result_objects[name] = perf["result"]

    st.dataframe(table_data, use_container_width=True, hide_index=True)

    # Comparison chart
    fig_comp = render_comparison_chart(result_objects)
    st.pyplot(fig_comp, use_container_width=True)
    plt.close(fig_comp)

    # Show individual solution paths
    st.markdown("""
    <div class="section-header">
        <span class="icon">🗺️</span>
        Solution <span class="accent">Paths</span>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(result_objects))
    for col, (name, res) in zip(cols, result_objects.items()):
        with col:
            st.markdown(f"""
            <div style="text-align:center; margin-bottom:0.5rem;">
                <span class="algo-badge">{name}</span>
            </div>
            """, unsafe_allow_html=True)
            if res.found:
                fig_s = render_solution(
                    maze_obj.grid, res.path,
                    start=maze_obj.start, end=maze_obj.end,
                )
                st.pyplot(fig_s, use_container_width=False)
                plt.close(fig_s)
            else:
                st.warning("No path")


# ═══════════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="footer">
    <p>
        Built with <span class="brand">Maze Solver AI</span> · 
        Python · Streamlit · NumPy · Matplotlib
    </p>
    <p style="margin-top:0.3rem; font-size:0.7rem;">
        BFS · DFS · A* Search · Real-time Animation · Performance Dashboard
    </p>
</div>
""", unsafe_allow_html=True)
