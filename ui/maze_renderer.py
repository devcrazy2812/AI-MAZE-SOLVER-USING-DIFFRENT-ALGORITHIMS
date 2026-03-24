"""
Pygame maze grid renderer with animation and interactivity.

Features:
    - Efficient grid rendering with per-cell state coloring
    - Animated pulsing markers on start/end
    - Click-to-place start and end points
    - Smooth visited-node color gradient based on discovery order
    - Cell hover highlighting
"""

import pygame
import math
import time
import numpy as np
from .theme import Colors, Dims, get_font, FontSizes


class MazeRenderer:
    """
    Renders a maze grid to a Pygame surface with rich animation.
    """

    def __init__(self, area_rect: pygame.Rect):
        self.area = area_rect
        self.grid = None
        self.cell_size = 10
        self.offset_x = 0
        self.offset_y = 0

        # Animation state
        self.visited = set()
        self.visited_order = {}  # pos -> discovery index (for gradient)
        self.frontier = set()
        self.current = None
        self.path = set()
        self.start = None
        self.end = None

        # Interactivity
        self.hovered_cell = None
        self.click_mode = None  # "start" or "end" or None
        self._pulse_time = 0

    def set_maze(self, grid: np.ndarray, start: tuple, end: tuple):
        """Load a new maze grid."""
        self.grid = grid
        self.start = start
        self.end = end
        self.clear_animation()
        self._compute_layout()

    def clear_animation(self):
        """Reset all animation state."""
        self.visited = set()
        self.visited_order = {}
        self.frontier = set()
        self.current = None
        self.path = set()

    def update_step(self, visited, frontier, current):
        """Update animation state from a SolveStep."""
        # Track discovery order for gradient
        for pos in visited:
            if pos not in self.visited_order:
                self.visited_order[pos] = len(self.visited_order)
        self.visited = visited
        self.frontier = frontier
        self.current = current

    def set_solution(self, path):
        """Show final solution path."""
        self.path = path
        self.frontier = set()
        self.current = None

    def cell_at_pixel(self, px, py):
        """Convert pixel coordinates to grid cell (row, col) or None."""
        if self.grid is None:
            return None
        c = (px - self.offset_x) // self.cell_size
        r = (py - self.offset_y) // self.cell_size
        rows, cols = self.grid.shape
        if 0 <= r < rows and 0 <= c < cols:
            return (r, c)
        return None

    def draw(self, surface: pygame.Surface):
        """Draw the maze with all overlays."""
        if self.grid is None:
            self._draw_placeholder(surface)
            return

        self._pulse_time = time.time()

        # Background
        pygame.draw.rect(surface, Colors.BG_PRIMARY, self.area)

        cs = self.cell_size
        rows, cols = self.grid.shape
        ox, oy = self.offset_x, self.offset_y

        # Update hovered cell
        mouse_pos = pygame.mouse.get_pos()
        if self.area.collidepoint(mouse_pos):
            self.hovered_cell = self.cell_at_pixel(*mouse_pos)
        else:
            self.hovered_cell = None

        # Clip to maze area
        surface.set_clip(self.area)

        total_visited = max(1, len(self.visited_order))

        for r in range(rows):
            for c in range(cols):
                x = ox + c * cs
                y = oy + r * cs

                # Skip offscreen cells
                if x + cs < self.area.left or x > self.area.right:
                    continue
                if y + cs < self.area.top or y > self.area.bottom:
                    continue

                cell_rect = pygame.Rect(x, y, cs, cs)
                pos = (r, c)
                color = self._get_cell_color(pos, total_visited)

                pygame.draw.rect(surface, color, cell_rect)

                # Hover highlight
                if pos == self.hovered_cell and self.grid[r, c] == 1:
                    s = pygame.Surface((cs, cs), pygame.SRCALPHA)
                    s.fill((255, 255, 255, 30))
                    surface.blit(s, (x, y))

        # Grid lines (for larger cells)
        if cs >= 8:
            line_color = (20, 25, 40)
            for r_line in range(rows + 1):
                yy = oy + r_line * cs
                pygame.draw.line(surface, line_color,
                                (ox, yy), (ox + cols * cs, yy), 1)
            for c_line in range(cols + 1):
                xx = ox + c_line * cs
                pygame.draw.line(surface, line_color,
                                (xx, oy), (xx, oy + rows * cs), 1)

        # Pulsing Start/End markers
        if self.start:
            self._draw_pulsing_marker(surface, self.start, Colors.START, "S")
        if self.end:
            self._draw_pulsing_marker(surface, self.end, Colors.END, "E")

        # Hovered cell info
        if self.hovered_cell and cs >= 10:
            self._draw_cell_info(surface, self.hovered_cell)

        surface.set_clip(None)

    def _get_cell_color(self, pos, total_visited):
        """Determine color for a cell with gradient support for visited nodes."""
        r, c = pos

        # Wall
        if self.grid[r, c] == 0:
            return Colors.WALL

        # Solution path — bright green with slight gradient
        if pos in self.path:
            return Colors.SOLUTION

        # Current node — bright rose with pulse
        if pos == self.current:
            pulse = 0.5 + 0.5 * math.sin(self._pulse_time * 8)
            return _lerp_color(Colors.CURRENT, (255, 120, 150), pulse)

        # Frontier — amber/yellow
        if pos in self.frontier:
            return Colors.FRONTIER_SOLID

        # Visited — gradient from dark blue to light blue by discovery order
        if pos in self.visited:
            idx = self.visited_order.get(pos, 0)
            t = idx / total_visited
            early_color = (25, 50, 120)     # Dark blue (discovered first)
            late_color = (80, 140, 220)     # Light blue (discovered last)
            return _lerp_color(early_color, late_color, t)

        # Open path
        return Colors.PATH

    def _draw_pulsing_marker(self, surface, pos, color, label):
        """Draw an animated pulsing marker on start/end."""
        cs = self.cell_size
        r, c = pos
        x = self.offset_x + c * cs + cs // 2
        y = self.offset_y + r * cs + cs // 2

        # Pulse effect
        pulse = 0.5 + 0.5 * math.sin(self._pulse_time * 4)
        radius = max(cs // 3, 4)
        outer_r = radius + int(3 * pulse)

        # Outer glow ring
        if cs >= 6:
            glow_surf = pygame.Surface((outer_r * 2 + 8, outer_r * 2 + 8),
                                       pygame.SRCALPHA)
            glow_alpha = int(80 * pulse)
            pygame.draw.circle(glow_surf, (*color[:3], glow_alpha),
                             (outer_r + 4, outer_r + 4), outer_r + 3)
            surface.blit(glow_surf, (x - outer_r - 4, y - outer_r - 4))

        # Main circle
        pygame.draw.circle(surface, color, (x, y), radius)

        # Inner bright
        inner_r = max(radius - 3, 2)
        bright = _lerp_color(color, (255, 255, 255), 0.3)
        pygame.draw.circle(surface, bright, (x - 1, y - 1), inner_r)

        # Label
        if cs >= 16:
            font = get_font(max(cs // 2, 9), bold=True)
            text = font.render(label, True, Colors.WHITE)
            text_rect = text.get_rect(center=(x, y))
            surface.blit(text, text_rect)

    def _draw_cell_info(self, surface, cell):
        """Draw coordinate info near hovered cell."""
        r, c = cell
        cs = self.cell_size
        x = self.offset_x + c * cs
        y = self.offset_y + r * cs

        font = get_font(FontSizes.TINY)
        info = f"({r},{c})"

        if cell == self.start:
            info += " START"
        elif cell == self.end:
            info += " END"
        elif cell in self.path:
            info += " PATH"
        elif cell in self.visited:
            info += " VISITED"

        text = font.render(info, True, Colors.TEXT_ACCENT)
        # Position tooltip above cell
        tx = x
        ty = y - 16
        if ty < self.area.top + 4:
            ty = y + cs + 4

        bg_rect = pygame.Rect(tx - 2, ty - 1,
                              text.get_width() + 4, text.get_height() + 2)
        pygame.draw.rect(surface, (10, 14, 26, 200), bg_rect, border_radius=3)
        surface.blit(text, (tx, ty))

    def _draw_placeholder(self, surface):
        """Draw empty state with instructional text."""
        pygame.draw.rect(surface, Colors.BG_PRIMARY, self.area)

        cx, cy = self.area.center

        # Animated maze icon
        t = time.time()
        pulse = 0.5 + 0.5 * math.sin(t * 2)
        icon_alpha = int(100 + 80 * pulse)

        # Draw grid pattern as placeholder
        grid_size = 5
        cell = 16
        gx = cx - (grid_size * cell) // 2
        gy = cy - 30 - (grid_size * cell) // 2

        pattern = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 1, 1, 1, 1],
        ]
        for rr in range(grid_size):
            for cc in range(grid_size):
                rect = pygame.Rect(gx + cc * cell, gy + rr * cell, cell - 1, cell - 1)
                if pattern[rr][cc] == 1:
                    col = _lerp_color(Colors.ACCENT_INDIGO, Colors.ACCENT_PURPLE, pulse)
                    s = pygame.Surface((cell - 1, cell - 1), pygame.SRCALPHA)
                    s.fill((*col, icon_alpha))
                    surface.blit(s, rect.topleft)
                else:
                    pygame.draw.rect(surface, Colors.BG_TERTIARY, rect, border_radius=2)

        font = get_font(FontSizes.HEADING)
        text = font.render("Press R to generate a maze", True, Colors.TEXT_MUTED)
        text_rect = text.get_rect(center=(cx, cy + 50))
        surface.blit(text, text_rect)

        sub = get_font(FontSizes.SMALL)
        sub_text = sub.render("or upload a maze image from the sidebar", True,
                             Colors.TEXT_MUTED)
        sub_rect = sub_text.get_rect(center=(cx, cy + 72))
        surface.blit(sub_text, sub_rect)

    def _compute_layout(self):
        """Compute cell size and offset for centering."""
        if self.grid is None:
            return
        rows, cols = self.grid.shape
        padding = 20
        avail_w = self.area.width - 2 * padding
        avail_h = self.area.height - 2 * padding
        cs_w = avail_w // cols
        cs_h = avail_h // rows
        self.cell_size = max(Dims.MIN_CELL_SIZE,
                            min(Dims.MAX_CELL_SIZE, min(cs_w, cs_h)))
        maze_w = cols * self.cell_size
        maze_h = rows * self.cell_size
        self.offset_x = self.area.x + (self.area.width - maze_w) // 2
        self.offset_y = self.area.y + (self.area.height - maze_h) // 2


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB colors."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))
