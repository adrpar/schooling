from pathlib import Path
from typing import Optional

import lxml.etree as ET

from exercises.zahlenmauer.algorithm import ZahlenmauerAlgorithm, ZahlenmauerPuzzle
from svg.svg_groups import distribute_groups_in_drawing_area
from svg.template import Template, validate_template

__all__ = ["ZahlenmauerTemplate"]

# Geometry lookup per base size (W, H) in mm/user units
BRICK_GEOMETRY = {
    3: (24.0, 15.0),
    4: (20.0, 13.0),
    5: (16.0, 11.0),
    6: (13.5, 9.5),
}

# Styling constants
BORDER_COLOR = "#2d3748"
BORDER_WIDTH = "0.35"
CORNER_RADIUS = "1.2"

GIVEN_TEXT_COLOR = "#1a202c"
SOLUTION_TEXT_COLOR = "#2b6cb0"
LABEL_COLOR = "#718096"

CLUE_FILL = "#edf2f7"       # Subtle soft gray for given numbers
BLANK_FILL = "#ffffff"      # Pure white for student writing space
SOLUTION_FILL = "#ebf8ff"   # Soft blue for solved answers


class ZahlenmauerTemplate:
    """Generic SVG template for Zahlenmauer puzzles using Template class."""
    
    def __init__(self, template_path: Optional[str | Path] = None):
        self.template = Template(template_path or Path(__file__).parent / "template" / "zahlenmauer.svg")

    def create_sheets(
        self,
        algorithm: ZahlenmauerAlgorithm,
        student_path: str,
        solution_path: Optional[str] = None,
    ):
        """
        Renders the generated Zahlenmauer puzzles into SVG files.

        :param algorithm: Algorithm instance containing generated puzzles.
        :param student_path: Destination path for the student sheet SVG.
        :param solution_path: Optional destination path for the solution sheet SVG.
        """
        puzzles = algorithm.puzzles if algorithm.puzzles else algorithm.build()

        # 1. Render Student Sheet
        student_template = self._render_canvas(puzzles, is_solution=False)
        student_template.write(student_path)

        # 2. Render Solution Sheet if requested
        if solution_path:
            solution_template = self._render_canvas(puzzles, is_solution=True)
            solution_template.write(solution_path)

    def _render_canvas(
        self, puzzles: list[ZahlenmauerPuzzle], is_solution: bool
    ) -> Template:
        template = Template(str(Path(__file__).parent / "template" / "zahlenmauer.svg"))
        
        drawing_area_node = template.get_element_by_id("drawingArea")
        drawing_area_rect = template.find_by_tag_and_attribute(
            drawing_area_node, "rect", "id"
        )

        # Update title for solution sheet
        title_elements = template.find_all_by_tag("tspan", template.get_element_by_id("Title"))
        if title_elements and is_solution:
            title_elements[0].set_text("Zahlenmauer — Lösung")

        # Generate pyramid SVG groups
        pyramid_groups = [
            self._render_single_pyramid(puzzle, idx + 1, is_solution)
            for idx, puzzle in enumerate(puzzles)
        ]

        # Distribute on the canvas
        distribute_groups_in_drawing_area(
            pyramid_groups, drawing_area_rect, drawing_area_node
        )

        return template

    def _render_single_pyramid(
        self, puzzle: ZahlenmauerPuzzle, index: int, is_solution: bool
    ) -> ET.Element:
        """
        Builds a single Zahlenmauer pyramid group.
        """
        B = puzzle.base_size
        W, H = BRICK_GEOMETRY.get(B, (20.0, 13.0))

        font_size = round(H * 0.48, 1)  # ~6.2px for H=13
        label_size = 3.2

        pyramid_group = ET.Element(
            "g",
            id=f"pyramid_{index}",
            transform="translate(0,0)",
        )

        # Label above the pyramid
        label = ET.SubElement(
            pyramid_group,
            "text",
            attrib={
                "x": "0",
                "y": "-2.5",
                "style": f"font-size:{label_size}px;font-family:Arial,Helvetica,sans-serif;fill:{LABEL_COLOR};font-weight:bold;",
            },
        )
        label.text = f"#{index}"

        # Draw bricks row by row from bottom (r=0) to apex (r=B-1)
        for r in range(B):
            num_bricks = B - r
            row_x = r * (W / 2.0)
            row_y = (B - 1 - r) * H

            for c in range(num_bricks):
                brick_x = row_x + c * W
                brick_y = row_y

                masked_val = puzzle.masked_wall[r][c]
                full_val = puzzle.full_wall[r][c]
                is_given = masked_val is not None

                # Determine brick fill and display text
                if is_solution:
                    fill = CLUE_FILL if is_given else SOLUTION_FILL
                    text_color = GIVEN_TEXT_COLOR if is_given else SOLUTION_TEXT_COLOR
                    display_text = str(full_val)
                else:
                    fill = CLUE_FILL if is_given else BLANK_FILL
                    text_color = GIVEN_TEXT_COLOR
                    display_text = str(masked_val) if is_given else ""

                # <rect> brick outline
                ET.SubElement(
                    pyramid_group,
                    "rect",
                    attrib={
                        "x": f"{brick_x:.2f}",
                        "y": f"{brick_y:.2f}",
                        "width": f"{W:.2f}",
                        "height": f"{H:.2f}",
                        "rx": CORNER_RADIUS,
                        "ry": CORNER_RADIUS,
                        "style": f"fill:{fill};stroke:{BORDER_COLOR};stroke-width:{BORDER_WIDTH};",
                    },
                )

                # <text> value centered vertically and horizontally
                if display_text:
                    # Slightly adjust font size if 3 digits to ensure generous margins
                    char_len = len(display_text)
                    curr_font_size = font_size if char_len <= 2 else font_size * 0.88

                    text_elem = ET.SubElement(
                        pyramid_group,
                        "text",
                        attrib={
                            "x": f"{brick_x + W / 2.0:.2f}",
                            "y": f"{brick_y + H / 2.0:.2f}",
                            "style": (
                                f"font-size:{curr_font_size:.1f}px;"
                                f"font-family:Arial,Helvetica,sans-serif;"
                                f"text-anchor:middle;"
                                f"dominant-baseline:central;"
                                f"font-weight:bold;"
                                f"fill:{text_color};"
                            ),
                        },
                    )
                    text_elem.text = display_text

        return pyramid_group
