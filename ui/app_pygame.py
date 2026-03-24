"""
Maze Solver AI -- Professional Pygame Desktop Application
==========================================================
Complete UI with layout system, animation engine, event handling,
toast notifications, progress indicator, and rich interactivity.

Run with:
    python ui/app_pygame.py

Keyboard Shortcuts:
    1       = Select BFS
    2       = Select DFS
    3       = Select A* (Manhattan)
    4       = Select A* (Euclidean)
    R       = Generate new maze
    SPACE   = Solve maze
    C       = Reset/Clear
    S       = Save screenshot
    UP/DOWN = Adjust animation speed
    ESC     = Cancel solving
"""

import pygame
import sys
import os
import math
import time as time_module

# Path setup
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from core.maze import Maze
from core.maze_generator import generate_maze
from algorithms import bfs, dfs, astar
from algorithms.base import SolveStep
from utils.performance import measure_performance

from ui.theme import (
    Colors, Dims, FontSizes, get_font, get_mono_font,
    WINDOW_WIDTH, WINDOW_HEIGHT, CONTROL_PANEL_WIDTH,
    STATUS_BAR_HEIGHT, MAZE_AREA_WIDTH, MAZE_AREA_HEIGHT,
)
from ui.widgets import (
    Button, Slider, Dropdown, StatDisplay,
    ProgressRing, Toast, Tooltip,
)
from ui.maze_renderer import MazeRenderer


class MazeSolverApp:
    """Main Pygame application."""

    ALGO_OPTIONS = ["BFS", "DFS", "A* (Manhattan)", "A* (Euclidean)"]
    ALGO_MAP = {
        "BFS": ("bfs", {}),
        "DFS": ("dfs", {}),
        "A* (Manhattan)": ("astar", {"heuristic": "manhattan"}),
        "A* (Euclidean)": ("astar", {"heuristic": "euclidean"}),
    }

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Maze Solver AI - Pathfinding Visualizer")
        self._set_icon()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # State
        self.maze = None
        self.status = "Ready -- Press R to generate a maze"
        self.status_color = Colors.TEXT_SECONDARY
        self.solving = False
        self.stepper = None
        self.step_count = 0
        self.solve_start_time = 0
        self._last_step_time = 0

        # Layout
        self.maze_area = pygame.Rect(0, 0, MAZE_AREA_WIDTH, MAZE_AREA_HEIGHT)
        self.panel_area = pygame.Rect(MAZE_AREA_WIDTH, 0,
                                      CONTROL_PANEL_WIDTH, WINDOW_HEIGHT)
        self.status_area = pygame.Rect(0, WINDOW_HEIGHT - STATUS_BAR_HEIGHT,
                                       MAZE_AREA_WIDTH, STATUS_BAR_HEIGHT)

        # Sub-systems
        self.renderer = MazeRenderer(self.maze_area)
        self.toast = Toast()
        self._header_hue = 0.0

        self._create_widgets()

    def _set_icon(self):
        try:
            icon = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(icon, Colors.ACCENT_PURPLE, (2, 2, 28, 28),
                           border_radius=6)
            pygame.draw.rect(icon, Colors.WHITE, (8, 8, 4, 4))
            pygame.draw.rect(icon, Colors.ACCENT_EMERALD, (20, 20, 4, 4))
            pygame.draw.line(icon, Colors.WHITE, (12, 10), (20, 10), 2)
            pygame.draw.line(icon, Colors.WHITE, (20, 10), (20, 20), 2)
            pygame.display.set_icon(icon)
        except Exception:
            pass

    def _create_widgets(self):
        px = MAZE_AREA_WIDTH + Dims.PANEL_PADDING
        pw = CONTROL_PANEL_WIDTH - 2 * Dims.PANEL_PADDING
        y = 70

        # Algorithm Dropdown
        self.algo_dropdown = Dropdown(
            (px, y + 18, pw, 36), self.ALGO_OPTIONS,
            selected=0, label="ALGORITHM"
        )
        y += 75

        # Maze Size Slider
        self.size_slider = Slider(
            (px, y + 18, pw, 20),
            min_val=11, max_val=101, value=31, step=2,
            label="MAZE SIZE", tooltip="Odd values only for proper maze walls"
        )
        y += 55

        # Speed Slider
        self.speed_slider = Slider(
            (px, y + 18, pw, 20),
            min_val=1, max_val=200, value=50, step=5,
            label="SPEED (ms/step)", suffix=" ms",
            tooltip="Lower = faster animation"
        )
        y += 65

        # Action Buttons
        btn_w = (pw - 10) // 2
        self.btn_generate = Button(
            (px, y, btn_w, Dims.BTN_HEIGHT),
            "Generate", self._on_generate, primary=True,
            tooltip="Generate a new random maze (R)"
        )
        self.btn_solve = Button(
            (px + btn_w + 10, y, btn_w, Dims.BTN_HEIGHT),
            "Solve", self._on_solve, primary=True,
            tooltip="Solve with selected algorithm (SPACE)"
        )
        y += Dims.BTN_HEIGHT + Dims.ITEM_GAP

        self.btn_reset = Button(
            (px, y, btn_w, Dims.BTN_HEIGHT),
            "Reset", self._on_reset,
            tooltip="Clear solution, keep maze (C)"
        )
        self.btn_screenshot = Button(
            (px + btn_w + 10, y, btn_w, Dims.BTN_HEIGHT),
            "Screenshot", self._on_screenshot,
            tooltip="Save as PNG (S)"
        )
        y += Dims.BTN_HEIGHT + Dims.SECTION_GAP + 8

        # Stats
        stat_w = (pw - 8) // 2
        self.stat_path = StatDisplay(px, y, stat_w, ">>", "Path Length")
        self.stat_nodes = StatDisplay(px + stat_w + 8, y, stat_w,
                                      "**", "Explored")
        y += 60
        self.stat_time = StatDisplay(px, y, stat_w, "~", "Time", " ms")
        self.stat_memory = StatDisplay(px + stat_w + 8, y, stat_w,
                                       "#", "Memory", " KB")
        self.stats = [self.stat_path, self.stat_nodes,
                      self.stat_time, self.stat_memory]
        y += 68

        # Progress Ring (shown during solving)
        self.progress_ring = ProgressRing(
            (MAZE_AREA_WIDTH + CONTROL_PANEL_WIDTH // 2, y + 22), radius=18
        )
        self.legend_y = y + 50

        # Button list
        self.buttons = [self.btn_generate, self.btn_solve,
                        self.btn_reset, self.btn_screenshot]

    # ════════════════════════════════════════════════════════════════
    #  MAIN LOOP
    # ════════════════════════════════════════════════════════════════

    def run(self):
        while self.running:
            self.clock.tick(60)
            self._handle_events()
            self._update_animation()
            self._render()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

    # ════════════════════════════════════════════════════════════════
    #  EVENTS
    # ════════════════════════════════════════════════════════════════

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Dropdown first (z-order)
            if self.algo_dropdown.handle_event(event):
                continue

            # Sliders
            if self.size_slider.handle_event(event):
                continue
            if self.speed_slider.handle_event(event):
                continue

            # Buttons
            for btn in self.buttons:
                if btn.handle_event(event):
                    break

            # Click on maze to set start/end
            if (event.type == pygame.MOUSEBUTTONDOWN and
                    self.maze_area.collidepoint(event.pos) and
                    not self.solving):
                self._handle_maze_click(event)

            # Keys
            if event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key):
        if key == pygame.K_1:
            self.algo_dropdown.selected = 0
            self._set_status("Algorithm: BFS", Colors.TEXT_ACCENT)
        elif key == pygame.K_2:
            self.algo_dropdown.selected = 1
            self._set_status("Algorithm: DFS", Colors.TEXT_ACCENT)
        elif key == pygame.K_3:
            self.algo_dropdown.selected = 2
            self._set_status("Algorithm: A* (Manhattan)", Colors.TEXT_ACCENT)
        elif key == pygame.K_4:
            self.algo_dropdown.selected = 3
            self._set_status("Algorithm: A* (Euclidean)", Colors.TEXT_ACCENT)
        elif key == pygame.K_r:
            self._on_generate()
        elif key == pygame.K_SPACE:
            self._on_solve()
        elif key == pygame.K_c:
            self._on_reset()
        elif key == pygame.K_s:
            self._on_screenshot()
        elif key == pygame.K_UP:
            self.speed_slider.value = self.speed_slider.value - 10
            self.toast.show(f"Speed: {int(self.speed_slider.value)} ms/step",
                          Colors.ACCENT_CYAN, 1.0)
        elif key == pygame.K_DOWN:
            self.speed_slider.value = self.speed_slider.value + 10
            self.toast.show(f"Speed: {int(self.speed_slider.value)} ms/step",
                          Colors.ACCENT_CYAN, 1.0)
        elif key == pygame.K_ESCAPE:
            if self.solving:
                self.solving = False
                self.stepper = None
                self._set_status("Cancelled", Colors.ACCENT_AMBER)
                self.toast.show("Solving cancelled", Colors.ACCENT_AMBER, 1.5)

    def _handle_maze_click(self, event):
        """Handle left/right click on maze to set start or end."""
        if self.maze is None:
            return
        cell = self.renderer.cell_at_pixel(*event.pos)
        if cell is None:
            return
        r, c = cell
        if self.grid_data[r, c] == 0:  # can't place on wall
            return

        if event.button == 1:  # left click = start
            self.maze.start = cell
            self.renderer.start = cell
            self.toast.show(f"Start set to ({r},{c})", Colors.START, 1.5)
        elif event.button == 3:  # right click = end
            self.maze.end = cell
            self.renderer.end = cell
            self.toast.show(f"End set to ({r},{c})", Colors.END, 1.5)

        self.renderer.clear_animation()
        self._clear_stats()

    # ════════════════════════════════════════════════════════════════
    #  CALLBACKS
    # ════════════════════════════════════════════════════════════════

    def _on_generate(self):
        if self.solving:
            return
        rows = int(self.size_slider.value)
        cols = rows

        self._set_status("Generating maze...", Colors.ACCENT_AMBER)

        grid = generate_maze(rows, cols)
        self.maze = Maze.from_grid(grid)
        self.grid_data = grid
        self.renderer.set_maze(grid, self.maze.start, self.maze.end)
        self._clear_stats()

        self._set_status(
            f"Maze ready: {rows}x{cols} | {self.maze.open_cells} cells",
            Colors.ACCENT_EMERALD
        )
        self.toast.show(f"New {rows}x{cols} maze generated!", Colors.ACCENT_EMERALD)

    def _on_solve(self):
        if self.maze is None:
            self._set_status("No maze! Press R to generate.", Colors.ACCENT_ROSE)
            self.toast.show("Generate a maze first!", Colors.ACCENT_ROSE, 2.0)
            return
        if self.solving:
            return

        self.renderer.clear_animation()
        self._clear_stats()

        algo_name = self.algo_dropdown.value
        algo_key, kwargs = self.ALGO_MAP[algo_name]

        if algo_key == "bfs":
            self.stepper = bfs.solve_stepwise(self.maze)
        elif algo_key == "dfs":
            self.stepper = dfs.solve_stepwise(self.maze)
        elif algo_key == "astar":
            self.stepper = astar.solve_stepwise(self.maze, **kwargs)

        self.solving = True
        self.step_count = 0
        self.solve_start_time = time_module.perf_counter()
        self._last_step_time = pygame.time.get_ticks()

        self._set_status(f"Solving with {algo_name}...", Colors.ACCENT_CYAN)
        self.toast.show(f"Solving with {algo_name}...", Colors.ACCENT_CYAN, 2.0)

    def _on_reset(self):
        self.solving = False
        self.stepper = None
        self.step_count = 0
        self.progress_ring.progress = 0.0
        if self.maze is not None:
            self.renderer.clear_animation()
        self._clear_stats()
        self._set_status("Reset -- Ready to solve", Colors.TEXT_SECONDARY)
        self.toast.show("Reset complete", Colors.TEXT_SECONDARY, 1.0)

    def _on_screenshot(self):
        filename = f"maze_screenshot_{int(time_module.time())}.png"
        filepath = os.path.join(ROOT_DIR, filename)
        try:
            pygame.image.save(self.screen, filepath)
            self._set_status(f"Saved: {filename}", Colors.ACCENT_EMERALD)
            self.toast.show(f"Screenshot saved!", Colors.ACCENT_EMERALD, 2.0)
        except Exception as e:
            self._set_status(f"Save failed: {e}", Colors.ACCENT_ROSE)

    # ════════════════════════════════════════════════════════════════
    #  ANIMATION ENGINE
    # ════════════════════════════════════════════════════════════════

    def _update_animation(self):
        if not self.solving or self.stepper is None:
            return

        now = pygame.time.get_ticks()
        delay = int(self.speed_slider.value)

        if now - self._last_step_time < delay:
            return
        self._last_step_time = now

        try:
            step = next(self.stepper)
            self.step_count += 1

            self.renderer.update_step(step.visited, step.frontier, step.current)

            # Real-time stats
            elapsed = time_module.perf_counter() - self.solve_start_time
            self.stat_nodes.value = str(len(step.visited))
            self.stat_time.value = f"{elapsed * 1000:.1f}"

            # Progress ring
            total = self.maze.open_cells if self.maze else 1
            self.progress_ring.progress = min(1.0, len(step.visited) / total)

        except StopIteration:
            self.solving = False
            self.stepper = None
            elapsed = time_module.perf_counter() - self.solve_start_time
            self._finish_solve(elapsed)

    def _finish_solve(self, elapsed):
        algo_name = self.algo_dropdown.value
        algo_key, kwargs = self.ALGO_MAP[algo_name]

        if algo_key == "bfs":
            result = bfs.solve(self.maze)
        elif algo_key == "dfs":
            result = dfs.solve(self.maze)
        else:
            result = astar.solve(self.maze, **kwargs)

        self.progress_ring.progress = 1.0

        if result.found:
            path_set = set(result.path)
            self.renderer.set_solution(path_set)

            self.stat_path.value = str(result.stats["path_length"])
            self.stat_nodes.value = str(result.stats["nodes_explored"])
            self.stat_time.value = f"{result.stats['time_ms']:.2f}"
            self.stat_memory.value = f"{result.stats['memory_kb']:.1f}"

            msg = (f"Path found! Length: {result.stats['path_length']} | "
                   f"Explored: {result.stats['nodes_explored']} | "
                   f"Time: {result.stats['time_ms']:.2f} ms")
            self._set_status(msg, Colors.ACCENT_EMERALD)
            self.toast.show("Path found!", Colors.ACCENT_EMERALD, 3.0)
        else:
            self._set_status("No path exists!", Colors.ACCENT_ROSE)
            self.toast.show("No path exists in this maze!", Colors.ACCENT_ROSE, 3.0)

    # ════════════════════════════════════════════════════════════════
    #  RENDERING PIPELINE
    # ════════════════════════════════════════════════════════════════

    def _render(self):
        self.screen.fill(Colors.BG_PRIMARY)

        # 1. Maze
        self.renderer.draw(self.screen)

        # 2. Control panel
        self._draw_panel()

        # 3. Status bar
        self._draw_status_bar()

        # 4. Toast notifications (on top of everything)
        self.toast.draw(self.screen, MAZE_AREA_WIDTH // 2, 10)

        # 5. Tooltips (absolute top layer)
        Tooltip.get().draw(self.screen)

    def _draw_panel(self):
        # Background
        pygame.draw.rect(self.screen, Colors.BG_SURFACE, self.panel_area)
        pygame.draw.line(self.screen, Colors.BORDER_SUBTLE,
                        (self.panel_area.left, 0),
                        (self.panel_area.left, WINDOW_HEIGHT), 1)

        px = MAZE_AREA_WIDTH + Dims.PANEL_PADDING

        # Animated header
        self._draw_header(px)

        # Widgets
        self.size_slider.draw(self.screen)
        self.speed_slider.draw(self.screen)
        for btn in self.buttons:
            btn.draw(self.screen)
        for stat in self.stats:
            stat.draw(self.screen)

        # Progress ring (only when solving or just finished)
        if self.solving or self.progress_ring.progress > 0:
            self.progress_ring.draw(self.screen)

        # Legend
        self._draw_legend()

        # Dropdown (last, to overlap)
        self.algo_dropdown.draw(self.screen)

        # Shortcuts
        self._draw_shortcuts()

    def _draw_header(self, px):
        """Animated gradient header text."""
        t = time_module.time()
        self._header_hue = (self._header_hue + 0.002) % 1.0

        # Title
        title_font = get_font(FontSizes.TITLE, bold=True)
        title = title_font.render("Maze Solver AI", True, Colors.TEXT_PRIMARY)
        self.screen.blit(title, (px, 18))

        # Subtitle
        sub_font = get_font(FontSizes.TINY)
        sub = sub_font.render("PATHFINDING VISUALIZER", True, Colors.TEXT_MUTED)
        self.screen.blit(sub, (px, 44))

        # Animated accent line
        pulse = 0.5 + 0.5 * math.sin(t * 2)
        line_w = 50 + int(30 * pulse)
        c1 = Colors.ACCENT_INDIGO
        c2 = Colors.ACCENT_PURPLE
        color = _lerp_color(c1, c2, pulse)
        pygame.draw.rect(self.screen, color, (px, 60, line_w, 2),
                        border_radius=1)

    def _draw_legend(self):
        px = MAZE_AREA_WIDTH + Dims.PANEL_PADDING
        y = self.legend_y

        font = get_font(FontSizes.SMALL)
        label_font = get_font(FontSizes.TINY)

        header = label_font.render("COLOR LEGEND", True, Colors.ACCENT_PURPLE)
        self.screen.blit(header, (px, y))
        y += 20

        items = [
            (Colors.WALL, "Wall"),
            (Colors.PATH, "Open Path"),
            (Colors.START, "Start (LClick)"),
            (Colors.END, "End (RClick)"),
            (Colors.VISITED_SOLID, "Visited"),
            (Colors.FRONTIER_SOLID, "Frontier"),
            (Colors.CURRENT, "Current"),
            (Colors.SOLUTION, "Solution"),
        ]

        col_w = (CONTROL_PANEL_WIDTH - 2 * Dims.PANEL_PADDING) // 2
        for i, (color, name) in enumerate(items):
            col = i % 2
            row = i // 2
            lx = px + col * col_w
            ly = y + row * 22

            pygame.draw.rect(self.screen, color,
                           (lx, ly + 1, Dims.LEGEND_DOT_SIZE,
                            Dims.LEGEND_DOT_SIZE), border_radius=2)
            text = font.render(name, True, Colors.TEXT_SECONDARY)
            self.screen.blit(text, (lx + Dims.LEGEND_DOT_SIZE + 6, ly))

    def _draw_shortcuts(self):
        px = MAZE_AREA_WIDTH + Dims.PANEL_PADDING
        y = WINDOW_HEIGHT - STATUS_BAR_HEIGHT - 120

        label_font = get_font(FontSizes.TINY)
        font = get_font(FontSizes.TINY)
        key_font = get_mono_font(FontSizes.TINY)

        header = label_font.render("KEYBOARD SHORTCUTS", True,
                                   Colors.ACCENT_PURPLE)
        self.screen.blit(header, (px, y))
        y += 18

        shortcuts = [
            ("R", "Generate Maze"),
            ("SPACE", "Solve"),
            ("C", "Reset"),
            ("S", "Screenshot"),
            ("1/2/3/4", "Select Algorithm"),
            ("UP/DOWN", "Speed +/-"),
            ("ESC", "Cancel Solve"),
            ("L/R Click", "Set Start/End"),
        ]

        for key, desc in shortcuts:
            key_surf = key_font.render(key, True, Colors.TEXT_ACCENT)
            key_w = key_surf.get_width() + 8
            key_rect = pygame.Rect(px, y, key_w, 13)
            pygame.draw.rect(self.screen, Colors.BG_TERTIARY, key_rect,
                           border_radius=3)
            self.screen.blit(key_surf, (px + 4, y + 1))

            desc_surf = font.render(desc, True, Colors.TEXT_MUTED)
            self.screen.blit(desc_surf, (px + key_w + 6, y + 1))
            y += 13

    def _draw_status_bar(self):
        pygame.draw.rect(self.screen, Colors.STATUS_BG, self.status_area)
        pygame.draw.line(self.screen, Colors.STATUS_BORDER,
                        (0, self.status_area.top),
                        (MAZE_AREA_WIDTH, self.status_area.top), 1)

        font = get_font(FontSizes.SMALL)

        # Animated status dot
        t = time_module.time()
        if self.solving:
            pulse = 0.5 + 0.5 * math.sin(t * 6)
            dot_color = _lerp_color(Colors.ACCENT_AMBER, Colors.ACCENT_ROSE, pulse)
        else:
            dot_color = Colors.ACCENT_EMERALD

        pygame.draw.circle(self.screen, dot_color,
                          (12, self.status_area.centery), 4)

        # Status text
        text = font.render(self.status, True, self.status_color)
        self.screen.blit(text, (24, self.status_area.y + 12))

        # FPS
        fps = int(self.clock.get_fps())
        fps_text = get_mono_font(FontSizes.TINY).render(
            f"{fps} FPS", True, Colors.TEXT_MUTED)
        self.screen.blit(fps_text,
                        (MAZE_AREA_WIDTH - fps_text.get_width() - 12,
                         self.status_area.y + 14))

    # Helpers
    def _set_status(self, text, color=None):
        self.status = text
        if color:
            self.status_color = color

    def _clear_stats(self):
        for stat in self.stats:
            stat.value = "--"
        self.progress_ring.progress = 0.0


def _lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))


def main():
    app = MazeSolverApp()
    app.run()


if __name__ == "__main__":
    main()
