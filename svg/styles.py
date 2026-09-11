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

# Backward-compatible convenience aliases
BORDER_COLOR = COLOR_BORDER
BORDER_WIDTH = STROKE_WIDTH_NORMAL
GIVEN_TEXT_COLOR = COLOR_TEXT_PRIMARY
SOLUTION_TEXT_COLOR = COLOR_SOLUTION
LABEL_COLOR = COLOR_TEXT_SECONDARY
CLUE_FILL = FILL_CLUE
BLANK_FILL = FILL_BLANK
SOLUTION_FILL = FILL_SOLUTION
