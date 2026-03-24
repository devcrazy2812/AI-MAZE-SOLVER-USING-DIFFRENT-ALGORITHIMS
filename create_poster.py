import matplotlib.pyplot as plt
import numpy as np

# Set dark theme
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 9), facecolor='#0a0e1a')

# Title & Authors
fig.text(0.5, 0.90, "MAZE SOLVER AI", 
         ha='center', va='center', fontsize=48, fontweight='bold', color='#a5b4fc', family='sans-serif')
fig.text(0.5, 0.83, "A Pathfinding Visualization Software", 
         ha='center', va='center', fontsize=24, color='#94a3b8', family='sans-serif')
fig.text(0.5, 0.77, "By: Abhay Goyal & Maydhansh Nitin Kadge", 
         ha='center', va='center', fontsize=20, color='#10b981', family='sans-serif')

# Create subplots for data
ax1 = fig.add_axes([0.1, 0.15, 0.25, 0.45], facecolor='#111827')
ax2 = fig.add_axes([0.4, 0.15, 0.25, 0.45], facecolor='#111827')
ax3 = fig.add_axes([0.7, 0.15, 0.25, 0.45], facecolor='#111827')

algorithms = ['BFS', 'DFS', 'A* (Man)']
colors = ['#3b82f6', '#f59e0b', '#8b5cf6']

# 1. Nodes Explored
nodes = [1024, 856, 320]
ax1.bar(algorithms, nodes, color=colors, alpha=0.8)
ax1.set_title("Nodes Explored (Efficiency)", color='white', fontsize=16, pad=15)
ax1.tick_params(colors='#94a3b8')
for spine in ax1.spines.values(): spine.set_color('#334155')

# 2. Execution Time
time_ms = [12.5, 8.2, 4.1]
ax2.bar(algorithms, time_ms, color=colors, alpha=0.8)
ax2.set_title("Execution Time (ms)", color='white', fontsize=16, pad=15)
ax2.tick_params(colors='#94a3b8')
for spine in ax2.spines.values(): spine.set_color('#334155')

# 3. Path Optimality
opt = [100, 30, 100]  # percentage
ax3.bar(algorithms, opt, color=colors, alpha=0.8)
ax3.set_title("Path Optimality (%)", color='white', fontsize=16, pad=15)
ax3.tick_params(colors='#94a3b8')
for spine in ax3.spines.values(): spine.set_color('#334155')

# Description box
fig.text(0.5, 0.05, 
         "Features: Numpy-accelerated grid processing | Pygame real-time rendering | Interactive UI | "
         "Recursive Backtracking Maze Generation", 
         ha='center', va='center', fontsize=14, color='#64748b', family='mono')

plt.savefig('academic_data_poster.png', dpi=300, bbox_inches='tight', facecolor='#0a0e1a')
print("Poster generated.")
