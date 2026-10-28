from typing import Optional

from svg.number_paper.paper_cell import NumericalPaperCell
from svg.svg_handler import NAMESPACE_MAP, SvgElement

BOX_STROKE_WIDTH = 0.223193



class WrittenCalcExerciseBox:
    NAMESPACE_MAP = NAMESPACE_MAP

    OPERATORS = ["+", "-", "×", "÷"]

    NUM_SPACES_BETWEEN_MAX_NUMBER_AND_OPERATOR = 1
    NUM_SPACES_BEFORE_OPERATOR = 1

    def __init__(
        self,
        operation,
        values: list[int],
        exercise_number: Optional[int] = None,
    ):
        self.operation = operation
        self.values = values
        self.exercise_number = exercise_number

    def generateBox(self, exercise_number: Optional[int] = None) -> SvgElement:
        num = exercise_number if exercise_number is not None else self.exercise_number
        return_element = SvgElement(
            "g", attrib={"id": "exerciseBox", "transform": "translate(0.0,0.0)"}
        )

        if num is not None:
            from svg.canvas_template import CanvasExerciseTemplate

            label = CanvasExerciseTemplate.create_exercise_label(num, x=0.0, y=-2.2)
            return_element.append(label)

        max_value = max(self.values)
        num_boxes = (
            len(str(max_value))
            + self.NUM_SPACES_BETWEEN_MAX_NUMBER_AND_OPERATOR + 1 
            + self.NUM_SPACES_BEFORE_OPERATOR
        )  # 1 for operator

        num_rows = len(self.values) + 1 + 1  # 1 for space and 1 for answer

        self._add_box_matrix(return_element, self.values, num_boxes, num_rows)

        return return_element


    def _add_box_matrix(self, node: SvgElement, values, num_x, num_y):
        number_box = NumericalPaperCell(0)

        box_rect = number_box.rect

        box_width = float(box_rect.attrib["width"])
        box_height = float(box_rect.attrib["height"])

        total_matrix_width = 0

        for j in range(num_y):
            current_value = self.values[j] if j < len(self.values) else ""

            new_origin_y = 0.0 + j * float(box_height)

            if j == 0:
                value_string = (num_x - len(str(current_value))) * " " + str(
                    current_value
                )
            else:
                num_spaces_and_operator = (
                    self.NUM_SPACES_BEFORE_OPERATOR
                    + 1
                    + self.NUM_SPACES_BETWEEN_MAX_NUMBER_AND_OPERATOR
                )
                value_string = (
                    " " * self.NUM_SPACES_BEFORE_OPERATOR
                    + (
                        self.OPERATORS[self.operation.value - 1]
                        if j < num_y - 2
                        else " "
                    )
                    + " " * self.NUM_SPACES_BETWEEN_MAX_NUMBER_AND_OPERATOR
                    + (num_x - len(str(current_value)) - num_spaces_and_operator) * " "
                    + str(current_value)
                )

            if j == num_y - 1:
                # add the thick line if this is the last row and the double line below
                self._draw_line(
                    node,
                    0.0 - BOX_STROKE_WIDTH,
                    j * float(box_height),
                    num_x * float(box_width) + BOX_STROKE_WIDTH,
                    j * float(box_height),
                    "single",
                )

                new_origin_y += 1.0

                self._draw_line(
                    node,
                    0.0 - BOX_STROKE_WIDTH,
                    new_origin_y + float(box_height) + 1.5,
                    num_x * float(box_width) + BOX_STROKE_WIDTH,
                    new_origin_y + float(box_height) + 1.5,
                    "double",
                )

            for i in range(num_x):
                new_box = NumericalPaperCell(value_string[i])

                new_origin_x = 0.0 + i * float(box_width)

                total_matrix_width = max(total_matrix_width, new_origin_x)

                new_box.group.attrib["transform"] = (
                    f"translate({new_origin_x},{new_origin_y})"
                )
                node.append(new_box.group)

    def _draw_line(
        self,
        svg_root: SvgElement,
        origin_x,
        origin_y,
        target_x,
        target_y,
        line_type="single",
    ):
        """
        Draws a single or double stroke line in an SVG.
        """
        # Single stroke line (black color, 2px width)
        if line_type == "single":
            svg_root.create_child(
                "line",
                attrib={
                    "x1": str(origin_x),
                    "y1": str(origin_y),
                    "x2": str(target_x),
                    "y2": str(target_y),
                    "style": "stroke:black;stroke-width:2",
                },
            )

        # Double stroke line (two lines - one for outer stroke and one for inner)
        elif line_type == "double":
            stroke_width = 0.5

            # Outer stroke
            svg_root.create_child(
                "line",
                attrib={
                    "x1": str(origin_x),
                    "y1": str(origin_y - 1.5 + stroke_width / 2),
                    "x2": str(target_x),
                    "y2": str(target_y - 1.5 + stroke_width / 2),
                    "style": f"stroke:black;stroke-width:{stroke_width}",
                },
            )

            # Inner stroke
            svg_root.create_child(
                "line",
                attrib={
                    "x1": str(origin_x),
                    "y1": str(origin_y + 1.5 + stroke_width / 2),
                    "x2": str(target_x),
                    "y2": str(target_y + 1.5 + stroke_width / 2),
                    "style": f"stroke:black;stroke-width:{stroke_width}",
                },
            )
