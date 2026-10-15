"""
Unified visual styling tokens for Rechenrally exercise sheets.
Tailored for elementary school worksheets: high-contrast, ink-friendly,
and clean modern aesthetics.
"""

# Palette
COLOR_BORDER = "#2d3748"           # Crisp dark slate for borders
COLOR_TEXT_PRIMARY = "#1a202c"     # Near-black for maximum readability
COLOR_TEXT_SECONDARY = "#718096"   # Muted neutral for #labels and footers
COLOR_SOLUTION = "#2b6cb0"         # Distinct blue for solution values

FILL_BLANK = "#ffffff"             # Pure white for student writing space
FILL_CLUE = "#edf2f7"              # Subtle light gray for given clue bricks
FILL_SOLUTION = "#ebf8ff"          # Soft blue highlight for solved values

# Typography
FONT_FAMILY = "Arial, Helvetica, sans-serif"

# Stroke & Geometry
STROKE_WIDTH_THIN = "0.22"
STROKE_WIDTH_NORMAL = "0.35"
STROKE_WIDTH_HEAVY = "2.0"
CORNER_RADIUS = "1.2"

# Worksheet Typography Sizes (in mm user-units)
FONT_SIZE_TITLE = "7.5"
FONT_SIZE_SUBTITLE = "3.6"
FONT_SIZE_LABEL = "3.2"
FONT_SIZE_FOOTER = "3.5"

# Worksheet layout coordinates (in mm on A4 210 x 297)
PAGE_WIDTH = 210.0
PAGE_HEIGHT = 297.0
HEADER_TITLE_X = 105.0
HEADER_TITLE_Y = 16.5
HEADER_SUBTITLE_Y = 22.5
FOOTER_DEFAULT_X = 15.0
FOOTER_DEFAULT_Y = 284.0

# Standard Text Prompts
DEFAULT_FOOTER_TEXT = "Name: ______________________    Datum: ____________"


def get_title_style() -> str:
    return (
        f"font-size:{FONT_SIZE_TITLE}px;font-family:{FONT_FAMILY};"
        f"font-weight:bold;fill:{COLOR_TEXT_PRIMARY};text-anchor:middle;"
    )


def get_subtitle_style() -> str:
    return (
        f"font-size:{FONT_SIZE_SUBTITLE}px;font-family:{FONT_FAMILY};"
        f"font-weight:normal;fill:{COLOR_TEXT_SECONDARY};text-anchor:middle;"
    )


def get_footer_style() -> str:
    return (
        f"font-size:{FONT_SIZE_FOOTER}px;font-family:{FONT_FAMILY};"
        f"fill:{COLOR_TEXT_SECONDARY};text-anchor:start;"
    )


def get_label_style() -> str:
    return (
        f"font-size:{FONT_SIZE_LABEL}px;font-family:{FONT_FAMILY};"
        f"font-weight:bold;fill:{COLOR_TEXT_SECONDARY};"
    )


# Backward-compatible convenience aliases
BORDER_COLOR = COLOR_BORDER
BORDER_WIDTH = STROKE_WIDTH_NORMAL
GIVEN_TEXT_COLOR = COLOR_TEXT_PRIMARY
SOLUTION_TEXT_COLOR = COLOR_SOLUTION
LABEL_COLOR = COLOR_TEXT_SECONDARY
CLUE_FILL = FILL_CLUE
BLANK_FILL = FILL_BLANK
SOLUTION_FILL = FILL_SOLUTION

