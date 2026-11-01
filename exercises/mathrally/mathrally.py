"""
exercises/mathrally/mathrally.py — structural constants for the Math Rally exercise.

Only the SVG template path/name constants live here now.  All tunable parameters
(operators, min/max values, seed) are exposed as CLI options in ``cli/mathrally.py``.
"""

from pathlib import Path

# Path to Inkscape-designed SVG templates (relative to repo root).
TEMPLATE_PATH = Path(__file__).parent.parent.parent / "img"
# Default template file name.
TEMPLATE_NAME = "Rally1.svg"
