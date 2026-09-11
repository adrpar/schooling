from pathlib import Path
from typing import Optional

import lxml.etree as ET

from exercises.zahlenmauer.algorithm import ZahlenmauerAlgorithm, ZahlenmauerPuzzle
from svg.svg_groups import distribute_groups_in_drawing_area

__all__ = ["ZahlenmauerTemplate"]

# Styling constants
BORDER_COLOR = "#2d3748"
BORDER_WIDTH = "0.35"
CORNER_RADIUS = "1.2"

GIVEN_TEXT_COLOR = "#1a202c"
SOLUTION_TEXT_COLOR = "#2b6cb0"
LABEL_COLOR = "#718096"

CLUE_FILL = "#edf2f7"     # Subtle soft gray for given numbers
BLANK_FILL = "#ffffff"    # Pure white for student writing space
SOLUTION_FILL = "#ebf8ff" # Soft blue for solved answers

# Drawing area dimensions (A4 minus margins, in viewBox user units = mm)
_DRAWING_WIDTH = 180.0
_DRAWING_HEIGHT = 242.0


def _get_brick_geometry(base_size: int) -> tuple[float, float]:
    """
    Compute brick width and height in user units (1 unit = 1 mm on A4).

    For small base sizes we use curated values. For larger sizes we
    auto-scale so the widest row (base_size bricks) always fits within
    the drawing area width, with a generous aspect ratio.
    """
    curated: dict[int, tuple[float, float]] = {
        3: (24.0, 15.0),
        4: (20.0, 13.0),
        5: (16.0, 11.0),
        6: (13.5, 9.5),
    }
    if base_size in curated:
        return curated[base_size]
    # Auto-scale: base row must fit in drawing width
    W = max(8.0, round(_DRAWING_WIDTH / base_size, 1))
    H = max(5.5, round(W * 0.65, 1))
    return W, H


class ZahlenmauerTemplate:
    """Renders Zahlenmauer (Addition Pyramid) puzzles as SVG sheets."""

    def __init__(self, template_path: Optional[str | Path] = None):
        self._svg_path = template_path or Path(__file__).parent / "drawing.svg"

    def create_sheets(
        self,
        algorithm: ZahlenmauerAlgorithm,
        student_path: str,
        solution_path: Optional[str] = None,
    ) -> None:
        """
        Renders puzzles into one or two SVG files (student + optional solution).

        :param algorithm: Algorithm instance with built puzzles.
        :param student_path: Destination path for the student sheet SVG.
        :param solution_path: Optional destination path for the solution sheet SVG.
        """
        puzzles = algorithm.puzzles if algorithm.puzzles else algorithm.build()

        self._render_canvas(puzzles, is_solution=False).write(str(student_path))
        if solution_path:
            self._render_canvas(puzzles, is_solution=True).write(str(solution_path))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _render_canvas(self, puzzles: list[ZahlenmauerPuzzle], is_solution: bool):
        """Build a complete SVG document for the given set of puzzles."""
        svg_xml = ET.parse(str(self._svg_path))
        svg_root = svg_xml.getroot()

        nsmap = {"svg": "http://www.w3.org/2000/svg"}

        def _find_by_id(elem_id: str):
            results = svg_root.findall(f".//*[@id='{elem_id}']")
            return results[0] if results else None

        # Optionally update page title for solution sheet
        title_group = _find_by_id("Title")
        if title_group is not None and is_solution:
            tspans = title_group.findall(".//svg:tspan", nsmap)
            if tspans:
                tspans[0].text = "Zahlenmauer — Lösung"

        # Locate drawing area
        drawing_area_node = _find_by_id("drawingArea")
        drawing_area_rect = None
        if drawing_area_node is not None:
            rects = drawing_area_node.findall("svg:rect", nsmap)
            drawing_area_rect = rects[0] if rects else None

        # Build pyramid groups
        pyramid_groups = [
            self._render_pyramid(puzzle, idx + 1, is_solution)
            for idx, puzzle in enumerate(puzzles)
        ]

        # Distribute groups across the drawing area
        if drawing_area_rect is not None and drawing_area_node is not None:
            distribute_groups_in_drawing_area(
                pyramid_groups, drawing_area_rect, drawing_area_node
            )

        return svg_xml

    def _render_pyramid(
        self, puzzle: ZahlenmauerPuzzle, index: int, is_solution: bool
    ) -> ET.Element:
        """Build a single pyramid <g> element."""
        B = puzzle.base_size
        W, H = _get_brick_geometry(B)
        font_size = round(H * 0.48, 1)

        group = ET.Element("g", id=f"pyramid_{index}", transform="translate(0,0)")

        # Small index label above the pyramid
        lbl = ET.SubElement(
            group,
            "text",
            attrib={
                "x": "0",
                "y": "-2.5",
                "style": (
                    f"font-size:3.2px;font-family:Arial,Helvetica,sans-serif;"
                    f"fill:{LABEL_COLOR};font-weight:bold;"
                ),
            },
        )
        lbl.text = f"#{index}"

        # Draw rows from bottom (r=0) to apex (r=B-1)
        for r in range(B):
            num_bricks = B - r
            row_x_offset = r * (W / 2.0)
            row_y = (B - 1 - r) * H

            for c in range(num_bricks):
                bx = row_x_offset + c * W
                by = row_y

                masked_val = puzzle.masked_wall[r][c]
                full_val = puzzle.full_wall[r][c]
                is_given = masked_val is not None

                if is_solution:
                    fill = CLUE_FILL if is_given else SOLUTION_FILL
                    text_color = GIVEN_TEXT_COLOR if is_given else SOLUTION_TEXT_COLOR
                    display = str(full_val)
                else:
                    fill = CLUE_FILL if is_given else BLANK_FILL
                    text_color = GIVEN_TEXT_COLOR
                    display = str(masked_val) if is_given else ""

                # Brick rectangle
                ET.SubElement(
                    group,
                    "rect",
                    attrib={
                        "x": f"{bx:.2f}",
                        "y": f"{by:.2f}",
                        "width": f"{W:.2f}",
                        "height": f"{H:.2f}",
                        "rx": CORNER_RADIUS,
                        "ry": CORNER_RADIUS,
                        "style": (
                            f"fill:{fill};stroke:{BORDER_COLOR};"
                            f"stroke-width:{BORDER_WIDTH};"
                        ),
                    },
                )

                # Centered number
                if display:
                    ch = len(display)
                    fs = font_size if ch <= 2 else font_size * 0.82
                    ET.SubElement(
                        group,
                        "text",
                        attrib={
                            "x": f"{bx + W / 2.0:.2f}",
                            "y": f"{by + H / 2.0:.2f}",
                            "style": (
                                f"font-size:{fs:.1f}px;"
                                f"font-family:Arial,Helvetica,sans-serif;"
                                f"text-anchor:middle;dominant-baseline:central;"
                                f"font-weight:bold;fill:{text_color};"
                            ),
                        },
                    ).text = display

        return group
