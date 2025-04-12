import lxml.etree as ET
from svg.number_paper.paper_cell import NumericalPaperCell

BOX_STROKE_WIDTH = 0.223193

class WrittenCalcExerciseBox:
    NAMESPACE_MAP = {
        "html": "http://www.w3.org/1999/xhtml",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xmlns": "http://www.w3.org/2000/xmlns/",
        None: "http://www.w3.org/2000/svg",
    }

    OPERATORS = ["+", "-", "×", "÷"]

    def __init__(self, operation, values: list[int]):
        self.operation = operation
        self.values = values

    def generateBox(self):
        return_element = ET.Element(
            "g", id="exerciseBox", transform="translate(0.0,0.0)"
        )

        max_value = max(self.values)
        num_boxes = (
            len(str(max_value)) + 2 + 2
        )  # 2 for space, 2 for the operator with space

        num_rows = len(self.values) + 1 + 1  # 1 for space and 1 for answer

        self._add_box_matrix(return_element, self.values, num_boxes, num_rows)

        return return_element

    def _add_box_matrix(self, node, values, num_x, num_y):
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
                value_string = (
                    " "
                    + (
                        self.OPERATORS[self.operation.value - 1]
                        if j < num_y - 2
                        else " "
                    )
                    + 2 * " "
                    + (num_x - len(str(current_value)) - 4) * " "
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

                new_box.group.attrib[
                    "transform"
                ] = f"translate({new_origin_x},{new_origin_y})"
                node.append(new_box.group)

    def _draw_line(
        self, svg_root, origin_x, origin_y, target_x, target_y, line_type="single"
    ):
        """
        Draws a single or double stroke line in an SVG.

        :param svg_root: The root element of the SVG document.
        :param origin_x: The x-coordinate of the line's origin.
        :param origin_y: The y-coordinate of the line's origin.
        :param target_x: The x-coordinate of the line's target.
        :param target_y: The y-coordinate of the line's target.
        :param line_type: Type of line ('single' or 'double').
        """

        # Single stroke line (black color, 2px width)
        if line_type == "single":
            line = ET.Element(
                "line",
                x1=str(origin_x),
                y1=str(origin_y),
                x2=str(target_x),
                y2=str(target_y),
                style="stroke:black;stroke-width:2",
            )
            svg_root.append(line)

        # Double stroke line (two lines - one for outer stroke and one for inner)
        elif line_type == "double":
            stroke_width = 0.5

            # Outer stroke (3px width)
            outer_line = ET.Element(
                "line",
                x1=str(origin_x),
                y1=str(origin_y - 1.5 + stroke_width / 2),
                x2=str(target_x),
                y2=str(target_y - 1.5 + stroke_width / 2),
                style="stroke:black;stroke-width:" + str(stroke_width),
            )
            svg_root.append(outer_line)

            # Inner stroke (2px width)
            inner_line = ET.Element(
                "line",
                x1=str(origin_x),
                y1=str(origin_y + 1.5 + stroke_width / 2),
                x2=str(target_x),
                y2=str(target_y + 1.5 + stroke_width / 2),
                style="stroke:black;stroke-width:" + str(stroke_width),
            )  # Inner line is white to create the double effect
            svg_root.append(inner_line)
