"""
Custom Pygame UI widgets with rich interactivity.

All widgets follow a consistent API:
    .draw(surface)       -- render the widget
    .handle_event(event) -- process mouse/key events
    .value               -- current state/value

Features:
    - Button: hover glow, press scale, tooltip, icon support
    - Slider: smooth drag, value preview, track glow
    - Dropdown: animated open/close, highlight selection
    - StatDisplay: icon, value, unit with card styling
    - Tooltip: auto-positioned tooltip on hover
    - ProgressRing: circular progress indicator
"""

import pygame
import math
import time
from .theme import Colors, Dims, get_font, get_mono_font, FontSizes


# ═══════════════════════════════════════════════════════════════════
#  TOOLTIP SYSTEM
# ═══════════════════════════════════════════════════════════════════

class Tooltip:
    """Delayed tooltip that appears on hover."""

    _instance = None  # singleton — only one tooltip visible at a time

    def __init__(self):
        self.text = ""
        self.visible = False
        self.pos = (0, 0)
        self._hover_start = 0
        self._delay = 0.5  # seconds

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def show(self, text, pos):
        if self.text != text:
            self.text = text
            self._hover_start = time.time()
            self.visible = False
        self.pos = pos
        if time.time() - self._hover_start >= self._delay:
            self.visible = True

    def hide(self):
        self.text = ""
        self.visible = False
        self._hover_start = 0

    def draw(self, surface):
        if not self.visible or not self.text:
            return
        font = get_font(FontSizes.TINY)
        text_surf = font.render(self.text, True, Colors.TEXT_PRIMARY)
        pw, ph = text_surf.get_width() + 16, text_surf.get_height() + 8
        x = min(self.pos[0], surface.get_width() - pw - 4)
        y = self.pos[1] - ph - 6

        # Shadow
        shadow = pygame.Rect(x + 2, y + 2, pw, ph)
        pygame.draw.rect(surface, (0, 0, 0), shadow, border_radius=6)
        # Background
        bg = pygame.Rect(x, y, pw, ph)
        pygame.draw.rect(surface, (30, 35, 55), bg, border_radius=6)
        pygame.draw.rect(surface, Colors.BORDER_ACTIVE, bg, 1, border_radius=6)
        surface.blit(text_surf, (x + 8, y + 4))


# ═══════════════════════════════════════════════════════════════════
#  BUTTON
# ═══════════════════════════════════════════════════════════════════

class Button:
    """
    Styled button with hover glow, press animation, and tooltip.
    """

    def __init__(self, rect, text, callback=None, primary=False,
                 icon=None, tooltip=""):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.primary = primary
        self.icon = icon
        self.tooltip_text = tooltip

        self.hovered = False
        self.pressed = False
        self.enabled = True
        self._press_time = 0
        self._anim_scale = 0.0  # 0..1 for hover glow

    def draw(self, surface):
        r = self.rect
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = r.collidepoint(mouse_pos) and self.enabled

        # Smooth hover animation
        target = 1.0 if self.hovered else 0.0
        self._anim_scale += (target - self._anim_scale) * 0.15

        # Press shrink effect
        draw_rect = r.copy()
        if self.pressed:
            draw_rect.inflate_ip(-4, -2)

        # Background color
        if not self.enabled:
            bg = Colors.BG_TERTIARY
            text_color = Colors.TEXT_MUTED
        elif self.primary:
            # Interpolate between two gradient colors based on hover
            t = self._anim_scale
            bg = _lerp_color(Colors.GRADIENT_BTN_1, Colors.GRADIENT_BTN_2, t)
            text_color = Colors.WHITE
        else:
            bg = _lerp_color(Colors.BG_SECONDARY, Colors.BG_HOVER, self._anim_scale)
            text_color = _lerp_color(Colors.TEXT_SECONDARY, Colors.TEXT_PRIMARY,
                                     self._anim_scale)

        # Hover glow (soft outline)
        if self._anim_scale > 0.05 and self.enabled:
            glow_rect = draw_rect.inflate(4, 4)
            glow_alpha = int(self._anim_scale * 40)
            glow_color = (*Colors.ACCENT_INDIGO[:3],)
            s = pygame.Surface((glow_rect.w, glow_rect.h), pygame.SRCALPHA)
            pygame.draw.rect(s, (*glow_color, glow_alpha), s.get_rect(),
                           border_radius=Dims.BTN_RADIUS + 2)
            surface.blit(s, glow_rect.topleft)

        # Main rect
        pygame.draw.rect(surface, bg, draw_rect, border_radius=Dims.BTN_RADIUS)

        # Border
        if not self.primary and self.enabled:
            border_col = _lerp_color(Colors.BORDER_SUBTLE, Colors.BORDER_ACTIVE,
                                     self._anim_scale)
            pygame.draw.rect(surface, border_col, draw_rect, 1,
                           border_radius=Dims.BTN_RADIUS)

        # Text + icon
        font = get_font(FontSizes.BODY, bold=self.primary)
        label = f"{self.icon} {self.text}" if self.icon else self.text
        text_surf = font.render(label, True, text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

        # Tooltip
        if self.hovered and self.tooltip_text:
            Tooltip.get().show(self.tooltip_text, mouse_pos)
        elif not self.hovered:
            tip = Tooltip.get()
            if tip.text == self.tooltip_text:
                tip.hide()

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self._press_time = time.time()
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos) and self.callback:
                    self.callback()
                    return True
        return False


# ═══════════════════════════════════════════════════════════════════
#  SLIDER
# ═══════════════════════════════════════════════════════════════════

class Slider:
    """Horizontal slider with smooth drag, glow track, and value display."""

    def __init__(self, rect, min_val, max_val, value, step=1,
                 label="", suffix="", tooltip=""):
        self.rect = pygame.Rect(rect)
        self.min_val = min_val
        self.max_val = max_val
        self._value = value
        self.step = step
        self.label = label
        self.suffix = suffix
        self.tooltip_text = tooltip
        self.dragging = False
        self._glow = 0.0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = max(self.min_val, min(self.max_val,
                          round(v / self.step) * self.step))

    def draw(self, surface):
        r = self.rect
        y_center = r.centery
        mouse_pos = pygame.mouse.get_pos()
        hovered = r.inflate(0, 20).collidepoint(mouse_pos)

        # Animate glow
        target = 1.0 if (hovered or self.dragging) else 0.0
        self._glow += (target - self._glow) * 0.15

        # Label + value
        font = get_font(FontSizes.SMALL)
        mono = get_mono_font(FontSizes.MONO)

        label_surf = font.render(self.label, True, Colors.TEXT_SECONDARY)
        surface.blit(label_surf, (r.x, r.y - 18))

        val_text = f"{int(self._value)}{self.suffix}"
        val_color = _lerp_color(Colors.TEXT_ACCENT,
                                Colors.ACCENT_CYAN, self._glow)
        val_surf = mono.render(val_text, True, val_color)
        surface.blit(val_surf, (r.right - val_surf.get_width(), r.y - 18))

        # Track
        track_h = Dims.SLIDER_HEIGHT
        track_rect = pygame.Rect(r.x, y_center - track_h // 2,
                                 r.width, track_h)
        pygame.draw.rect(surface, Colors.SLIDER_TRACK, track_rect,
                         border_radius=3)

        # Fill with gradient-like effect
        ratio = (self._value - self.min_val) / max(1, self.max_val - self.min_val)
        fill_w = int(r.width * ratio)
        if fill_w > 0:
            fill_color = _lerp_color(Colors.ACCENT_BLUE, Colors.ACCENT_PURPLE, ratio)
            fill_rect = pygame.Rect(r.x, y_center - track_h // 2,
                                    fill_w, track_h)
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=3)

        # Knob
        knob_x = r.x + fill_w
        knob_r = Dims.SLIDER_KNOB_R
        if self._glow > 0.05:
            # Outer glow ring
            glow_r = knob_r + int(4 * self._glow)
            s = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*Colors.ACCENT_INDIGO, int(50 * self._glow)),
                             (glow_r + 2, glow_r + 2), glow_r)
            surface.blit(s, (knob_x - glow_r - 2, y_center - glow_r - 2))

        pygame.draw.circle(surface, Colors.WHITE, (knob_x, y_center), knob_r)
        pygame.draw.circle(surface, Colors.ACCENT_INDIGO, (knob_x, y_center),
                          knob_r - 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            expanded = self.rect.inflate(0, 24)
            if expanded.collidepoint(event.pos):
                self.dragging = True
                self._update_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_from_mouse(event.pos[0])
            return True
        return False

    def _update_from_mouse(self, mouse_x):
        ratio = (mouse_x - self.rect.x) / max(1, self.rect.width)
        ratio = max(0.0, min(1.0, ratio))
        raw = self.min_val + ratio * (self.max_val - self.min_val)
        self.value = raw


# ═══════════════════════════════════════════════════════════════════
#  DROPDOWN
# ═══════════════════════════════════════════════════════════════════

class Dropdown:
    """Styled dropdown selector with highlight on selected item."""

    def __init__(self, rect, options, selected=0, label=""):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.selected = selected
        self.label = label
        self.open = False
        self._anim = 0.0

    @property
    def value(self):
        return self.options[self.selected]

    def draw(self, surface):
        r = self.rect
        font = get_font(FontSizes.BODY)
        small = get_font(FontSizes.SMALL)
        mouse_pos = pygame.mouse.get_pos()

        # Animate open/close
        target = 1.0 if self.open else 0.0
        self._anim += (target - self._anim) * 0.2

        # Label
        if self.label:
            label_surf = small.render(self.label, True, Colors.TEXT_SECONDARY)
            surface.blit(label_surf, (r.x, r.y - 18))

        # Main box
        hovered = r.collidepoint(mouse_pos)
        border = Colors.BORDER_ACTIVE if (self.open or hovered) else Colors.BORDER_SUBTLE
        pygame.draw.rect(surface, Colors.BG_SECONDARY, r, border_radius=Dims.BTN_RADIUS)
        pygame.draw.rect(surface, border, r, 1, border_radius=Dims.BTN_RADIUS)

        # Selected text
        text_surf = font.render(self.options[self.selected], True, Colors.TEXT_PRIMARY)
        surface.blit(text_surf, (r.x + 12, r.centery - text_surf.get_height() // 2))

        # Arrow indicator
        arrow_char = chr(9650) if self.open else chr(9660)  # ▲ ▼
        try:
            arrow_surf = font.render(arrow_char, True, Colors.TEXT_MUTED)
        except Exception:
            arrow_surf = font.render("v", True, Colors.TEXT_MUTED)
        surface.blit(arrow_surf, (r.right - 24,
                     r.centery - arrow_surf.get_height() // 2))

        # Dropdown list
        if self.open:
            for i, opt in enumerate(self.options):
                item_rect = pygame.Rect(r.x, r.bottom + i * r.height,
                                        r.width, r.height)
                item_hovered = item_rect.collidepoint(mouse_pos)

                if i == self.selected:
                    bg = Colors.ACCENT_INDIGO
                elif item_hovered:
                    bg = Colors.BG_HOVER
                else:
                    bg = Colors.BG_TERTIARY

                pygame.draw.rect(surface, bg, item_rect)
                pygame.draw.rect(surface, Colors.BORDER_SUBTLE, item_rect, 1)

                color = Colors.WHITE if i == self.selected else (
                    Colors.TEXT_PRIMARY if item_hovered else Colors.TEXT_SECONDARY
                )
                opt_surf = font.render(opt, True, color)
                surface.blit(opt_surf, (item_rect.x + 12,
                             item_rect.centery - opt_surf.get_height() // 2))

                # Checkmark for selected
                if i == self.selected:
                    check = font.render("*", True, Colors.WHITE)
                    surface.blit(check, (item_rect.right - 24,
                                 item_rect.centery - check.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.open:
                for i in range(len(self.options)):
                    item_rect = pygame.Rect(self.rect.x,
                                            self.rect.bottom + i * self.rect.height,
                                            self.rect.width, self.rect.height)
                    if item_rect.collidepoint(event.pos):
                        self.selected = i
                        self.open = False
                        return True
                self.open = False
                return False
            else:
                if self.rect.collidepoint(event.pos):
                    self.open = True
                    return True
        return False


# ═══════════════════════════════════════════════════════════════════
#  STAT DISPLAY
# ═══════════════════════════════════════════════════════════════════

class StatDisplay:
    """Metric card with icon, value, label, and hover highlight."""

    def __init__(self, x, y, width, icon, label, unit=""):
        self.x = x
        self.y = y
        self.width = width
        self.icon = icon
        self.label = label
        self.unit = unit
        self._value = "--"
        self._glow = 0.0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    def draw(self, surface):
        font = get_font(FontSizes.SMALL)
        mono = get_mono_font(FontSizes.HEADING)
        mouse_pos = pygame.mouse.get_pos()

        card = pygame.Rect(self.x, self.y, self.width, 52)
        hovered = card.collidepoint(mouse_pos)

        # Animate
        target = 1.0 if hovered else 0.0
        self._glow += (target - self._glow) * 0.12

        # Background
        bg = _lerp_color(Colors.BG_TERTIARY, Colors.BG_HOVER, self._glow)
        pygame.draw.rect(surface, bg, card, border_radius=8)

        border = _lerp_color(Colors.BORDER_SUBTLE, Colors.BORDER_ACTIVE, self._glow)
        pygame.draw.rect(surface, border, card, 1, border_radius=8)

        # Top accent line on hover
        if self._glow > 0.1:
            accent_w = int(self.width * self._glow)
            pygame.draw.rect(surface, Colors.ACCENT_INDIGO,
                           (self.x + (self.width - accent_w) // 2,
                            self.y, accent_w, 2), border_radius=1)

        # Label
        lbl = font.render(f"{self.icon} {self.label}", True, Colors.TEXT_MUTED)
        surface.blit(lbl, (self.x + 10, self.y + 6))

        # Value
        val_text = f"{self._value}{self.unit}"
        val_color = _lerp_color(Colors.TEXT_ACCENT, Colors.ACCENT_CYAN, self._glow)
        val_surf = mono.render(val_text, True, val_color)
        surface.blit(val_surf, (self.x + 10, self.y + 26))


# ═══════════════════════════════════════════════════════════════════
#  PROGRESS RING
# ═══════════════════════════════════════════════════════════════════

class ProgressRing:
    """Circular progress indicator widget."""

    def __init__(self, center, radius=18, thickness=3):
        self.center = center
        self.radius = radius
        self.thickness = thickness
        self.progress = 0.0  # 0..1
        self._angle = 0

    def draw(self, surface):
        cx, cy = self.center
        r = self.radius

        # Background circle
        pygame.draw.circle(surface, Colors.BG_TERTIARY, (cx, cy), r, self.thickness)

        # Progress arc
        if self.progress > 0:
            start_angle = -math.pi / 2
            end_angle = start_angle + 2 * math.pi * self.progress

            # Draw arc as small segments
            segments = max(4, int(60 * self.progress))
            points = []
            for i in range(segments + 1):
                angle = start_angle + (end_angle - start_angle) * i / segments
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                points.append((px, py))

            if len(points) >= 2:
                pygame.draw.lines(surface, Colors.ACCENT_EMERALD, False,
                                points, self.thickness)

        # Center text
        font = get_mono_font(FontSizes.TINY)
        pct = f"{int(self.progress * 100)}%"
        text = font.render(pct, True, Colors.TEXT_PRIMARY)
        text_rect = text.get_rect(center=(cx, cy))
        surface.blit(text, text_rect)

        # Spinning dot when active
        if 0 < self.progress < 1:
            self._angle = (self._angle + 3) % 360
            dot_angle = math.radians(self._angle) - math.pi / 2
            dx = cx + math.cos(dot_angle) * (r + 6)
            dy = cy + math.sin(dot_angle) * (r + 6)
            pygame.draw.circle(surface, Colors.ACCENT_CYAN, (int(dx), int(dy)), 3)


# ═══════════════════════════════════════════════════════════════════
#  NOTIFICATION TOAST
# ═══════════════════════════════════════════════════════════════════

class Toast:
    """Temporary popup notification."""

    def __init__(self):
        self.messages = []  # [(text, color, expire_time)]

    def show(self, text, color=Colors.ACCENT_EMERALD, duration=2.5):
        self.messages.append((text, color, time.time() + duration))

    def draw(self, surface, x, y):
        now = time.time()
        self.messages = [(t, c, e) for t, c, e in self.messages if e > now]

        font = get_font(FontSizes.SMALL)
        for i, (text, color, expire) in enumerate(self.messages):
            remaining = expire - now
            alpha = min(1.0, remaining / 0.5)  # fade out last 0.5s

            dy = y + i * 32
            text_surf = font.render(text, True, color)
            pw = text_surf.get_width() + 24
            ph = text_surf.get_height() + 10

            # Background
            s = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pygame.draw.rect(s, (17, 24, 39, int(220 * alpha)), s.get_rect(),
                           border_radius=8)
            pygame.draw.rect(s, (*color[:3], int(150 * alpha)), s.get_rect(),
                           1, border_radius=8)
            s.blit(font.render(text, True, (*color[:3],)), (12, 5))
            surface.blit(s, (x - pw // 2, dy))


# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════

def _lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB colors."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))
