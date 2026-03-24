"""
Theme configuration for the Pygame desktop application.

Defines all colors, fonts, dimensions, and layout constants
for a premium dark-mode UI.
"""

import pygame

# ═══════════════════════════════════════════════════════════════════
#  WINDOW LAYOUT
# ═══════════════════════════════════════════════════════════════════
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 760
CONTROL_PANEL_WIDTH = 320
STATUS_BAR_HEIGHT = 40
MAZE_AREA_WIDTH = WINDOW_WIDTH - CONTROL_PANEL_WIDTH
MAZE_AREA_HEIGHT = WINDOW_HEIGHT - STATUS_BAR_HEIGHT

# ═══════════════════════════════════════════════════════════════════
#  COLORS — Premium Dark Palette
# ═══════════════════════════════════════════════════════════════════
class Colors:
    # Backgrounds
    BG_PRIMARY      = (10, 14, 26)       # Deep navy
    BG_SECONDARY    = (17, 24, 39)       # Dark card bg
    BG_TERTIARY     = (30, 41, 59)       # Lighter card
    BG_SURFACE      = (22, 30, 48)       # Panel bg
    BG_HOVER        = (38, 50, 72)       # Hover state

    # Borders
    BORDER_SUBTLE   = (50, 60, 90)
    BORDER_ACTIVE   = (99, 102, 241)     # Indigo glow

    # Text
    TEXT_PRIMARY     = (241, 245, 249)
    TEXT_SECONDARY   = (148, 163, 184)
    TEXT_MUTED       = (100, 116, 139)
    TEXT_ACCENT      = (165, 180, 252)   # Light indigo

    # Accents
    ACCENT_PURPLE    = (139, 92, 246)
    ACCENT_BLUE      = (59, 130, 246)
    ACCENT_CYAN      = (6, 182, 212)
    ACCENT_EMERALD   = (16, 185, 129)
    ACCENT_ROSE      = (244, 63, 94)
    ACCENT_AMBER     = (245, 158, 11)
    ACCENT_INDIGO    = (99, 102, 241)

    # Gradients (for rendering as two-color tuples)
    GRADIENT_BTN_1   = (99, 102, 241)    # Indigo
    GRADIENT_BTN_2   = (139, 92, 246)    # Purple

    # Maze colors
    WALL             = (15, 18, 30)
    PATH             = (45, 55, 80)
    VISITED          = (59, 130, 246, 150)   # Blue (with alpha hint)
    VISITED_SOLID    = (40, 80, 160)
    FRONTIER         = (250, 204, 21)        # Yellow
    FRONTIER_SOLID   = (180, 150, 20)
    CURRENT          = (244, 63, 94)         # Rose
    SOLUTION         = (16, 185, 129)        # Emerald
    START            = (34, 197, 94)         # Green
    END              = (239, 68, 68)         # Red

    # Slider
    SLIDER_TRACK     = (50, 60, 90)
    SLIDER_FILL      = (99, 102, 241)
    SLIDER_KNOB      = (165, 180, 252)

    # Status bar
    STATUS_BG        = (8, 10, 20)
    STATUS_BORDER    = (40, 50, 75)

    # White / Black
    WHITE            = (255, 255, 255)
    BLACK            = (0, 0, 0)


# ═══════════════════════════════════════════════════════════════════
#  FONT SIZES
# ═══════════════════════════════════════════════════════════════════
class FontSizes:
    TITLE    = 22
    HEADING  = 16
    BODY     = 14
    SMALL    = 12
    TINY     = 10
    MONO     = 13


# ═══════════════════════════════════════════════════════════════════
#  UI DIMENSIONS
# ═══════════════════════════════════════════════════════════════════
class Dims:
    # Buttons
    BTN_HEIGHT       = 38
    BTN_RADIUS       = 8
    BTN_PADDING      = 12

    # Slider
    SLIDER_HEIGHT    = 6
    SLIDER_KNOB_R    = 8

    # Panel
    PANEL_PADDING    = 20
    SECTION_GAP      = 16
    ITEM_GAP         = 10

    # Legend
    LEGEND_DOT_SIZE  = 12
    LEGEND_GAP       = 6

    # Maze cell
    MIN_CELL_SIZE    = 4
    MAX_CELL_SIZE    = 30


# ═══════════════════════════════════════════════════════════════════
#  FONT LOADER
# ═══════════════════════════════════════════════════════════════════
_fonts_cache = {}

def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Get a cached pygame font. Falls back to system default."""
    key = (size, bold)
    if key not in _fonts_cache:
        try:
            # Try to use a nice system font
            name = pygame.font.match_font("segoeui" if not bold else "segoeui",
                                          bold=bold)
            if name:
                _fonts_cache[key] = pygame.font.Font(name, size)
            else:
                _fonts_cache[key] = pygame.font.SysFont("arial", size, bold=bold)
        except Exception:
            _fonts_cache[key] = pygame.font.SysFont(None, size, bold=bold)
    return _fonts_cache[key]


def get_mono_font(size: int) -> pygame.font.Font:
    """Get a monospaced font."""
    key = ("mono", size)
    if key not in _fonts_cache:
        try:
            name = pygame.font.match_font("consolas") or pygame.font.match_font("courier")
            if name:
                _fonts_cache[key] = pygame.font.Font(name, size)
            else:
                _fonts_cache[key] = pygame.font.SysFont("monospace", size)
        except Exception:
            _fonts_cache[key] = pygame.font.SysFont("monospace", size)
    return _fonts_cache[key]
