"""
svg — SVG construction, parsing, layout, and PDF rendering engine.

Provides:
- `SVGFile`: Wrapper around `lxml.etree` for loading, querying, mutating, and saving SVG documents.
- `CanvasTemplate`: Generates standardized A4 canvas DOM trees programmatically.
- `calculate_group_dimensions`, `distribute_groups_in_drawing_area`: Layout and bounding box calculation for SVG groups.
- `render_svg_to_pdf`: Inkscape-backed PDF export utility.
"""

from svg.canvas_template import CanvasExerciseTemplate
from svg.svg_groups import calculate_group_dimensions, distribute_groups_in_drawing_area
from svg.svg_handler import SVGFile, render_svg_to_pdf

__all__ = [
    "CanvasExerciseTemplate",
    "SVGFile",
    "calculate_group_dimensions",
    "distribute_groups_in_drawing_area",
    "render_svg_to_pdf",
]

