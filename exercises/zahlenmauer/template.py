from pathlib import Path
from typing import Optional, Union

from exercises.zahlenmauer.algorithm import ZahlenmauerAlgorithm, ZahlenmauerPuzzle
from svg.canvas_template import CanvasExerciseTemplate
from svg.styles import (
    BLANK_FILL,
    BORDER_COLOR,
    BORDER_WIDTH,
    CLUE_FILL,
    CORNER_RADIUS,
    FONT_FAMILY,
    GIVEN_TEXT_COLOR,
    LABEL_COLOR,
    SOLUTION_FILL,
    SOLUTION_TEXT_COLOR,
)
from svg.svg_handler import SvgElement

__all__ = ["ZahlenmauerTemplate"]

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


class ZahlenmauerTemplate(CanvasExerciseTemplate):
    """Renders Zahlenmauer (Addition Pyramid) puzzles as SVG sheets."""

    _DEFAULT_TEMPLATE = Path(__file__).parent / "drawing.svg"

    def __init__(self, template_path: Optional[Union[str, Path]] = None):
        super().__init__(template_path or self._DEFAULT_TEMPLATE)

    def create_sheets(
        self,
        algorithm: ZahlenmauerAlgorithm,
        student_path: Union[str, Path],
        solution_path: Optional[Union[str, Path]] = None,
        show_numbering: bool = True,
    ) -> None:
        """
        Renders puzzles into one or two SVG files (student + optional solution).

        :param algorithm: Algorithm instance with built puzzles.
        :param student_path: Destination path for the student sheet SVG.
        :param solution_path: Optional destination path for the solution sheet SVG.
        :param show_numbering: Whether to render '#1', '#2', etc. above each pyramid.
        """
        puzzles = algorithm.puzzles if algorithm.puzzles else algorithm.build()
        config_text = (
            f"Basis: {algorithm.base_size} Steine — "
            f"Stufe: {algorithm.difficulty.name.capitalize()} — "
            f"Seed: {algorithm.seed}"
        )

        # 1. Render student sheet
        student_canvas = self.clone()
        student_canvas.set_header("Zahlenmauer", config_text)
        student_canvas.set_footer(visible=True)
        student_pyramids = [
            self._render_pyramid(p, idx + 1, is_solution=False, show_numbering=show_numbering)
            for idx, p in enumerate(puzzles)
        ]
        student_canvas.distribute_exercises(student_pyramids)
        student_canvas.write(student_path)

        # 2. Render solution sheet if requested
        if solution_path:
            solution_canvas = self.clone()
            solution_canvas.set_header("Zahlenmauer — Lösung", config_text)
            solution_canvas.set_footer(visible=False)
            solution_pyramids = [
                self._render_pyramid(p, idx + 1, is_solution=True, show_numbering=show_numbering)
                for idx, p in enumerate(puzzles)
            ]
            solution_canvas.distribute_exercises(solution_pyramids)
            solution_canvas.write(solution_path)

    def _render_pyramid(
        self,
        puzzle: ZahlenmauerPuzzle,
        index: int,
        is_solution: bool,
        show_numbering: bool = True,
    ) -> SvgElement:
        """Build a single pyramid <g> element using SvgElement."""
        B = puzzle.base_size
        W, H = _get_brick_geometry(B)
        font_size = round(H * 0.48, 1)

        group = SvgElement("g", attrib={"id": f"pyramid_{index}", "transform": "translate(0,0)"})

        # Small index label above the pyramid
        if show_numbering:
            group.append(CanvasExerciseTemplate.create_exercise_label(index, x=0.0, y=-2.5))


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
                group.create_child(
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
                    group.create_child(
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
                        text=display,
                    )

        return group
