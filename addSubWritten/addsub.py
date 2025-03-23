from copy import deepcopy
from enum import Enum
from random import seed, randrange, choice

import lxml.etree as ET

import re

BOX_STROKE_WIDTH = 0.223193

BOX_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<g id="box_template" transform="translate(0.0,0.0)">
    <text xml:space="preserve" style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.93889px;font-family:Helvetica;-inkscape-font-specification:Helvetica;text-align:start;writing-mode:lr-tb;direction:ltr;text-anchor:start;fill:#000000;stroke-width:0.264583" x="1.5323327" y="4.7672572" id="text_template"><tspan sodipodi:role="line" id="tspan_template" style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.93889px;font-family:Helvetica;-inkscape-font-specification:Helvetica;stroke-width:0.264583" x="1.5323327" y="4.7672572">4</tspan></text>
    <rect style="fill:none;stroke:#000000;stroke-width:0.223193;stroke-dasharray:none;stroke-opacity:1" id="rect_template" width="5.8861966" height="5.8861966" x="0" y="0"/>
</g>
</svg>
"""


class Operator(Enum):
    ADDITION = 1
    SUBTRACTION = 2
    MULTIPLICATION = 3
    DIVISION = 4


# CONFIG SECTION

OPERATORS = [
    Operator.ADDITION,
    Operator.SUBTRACTION,
    # Operator.MULTIPLICATION,
    # Operator.DIVISION,
]
MIN_VALUE = 1
MAX_VALUE = 999
SEED = 7874
NUM_EXERCISES = 30
NUM_ROWS_PER_EXERCISE = 2


class SVGFile(object):
    NAMESPACE_MAP = {
        "html": "http://www.w3.org/1999/xhtml",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xmlns": "http://www.w3.org/2000/xmlns/",
        None: "http://www.w3.org/2000/svg",
    }

    def __init__(self):
        self.svg_xml = ET.parse("addSubWritten/drawing.svg")
        self.svg = self.svg_xml.getroot()

    def find_all(self, tag):
        return self.svg.findall(".//{}".format(tag), namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes(self, tag, attribute):
        elements = self.find_all(tag)
        return {element.attrib[attribute]: element for element in elements}

    def find_all_in_node(self, node, tag):
        return node.findall(".//{}".format(tag), namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes_in_node(self, node, tag, attribute):
        elements = self.find_all_in_node(node, tag)
        return {element.attrib[attribute]: element for element in elements}

    def all_spans_in_text(self, text_node):
        return text_node.findall(".//tspan", namespaces=self.NAMESPACE_MAP)

    def write(self, file_name):
        self.svg_xml.write(file_name)


class SvgNode(object):
    NAMESPACE_MAP = {
        "html": "http://www.w3.org/1999/xhtml",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xmlns": "http://www.w3.org/2000/xmlns/",
        None: "http://www.w3.org/2000/svg",
    }

    def __init__(self, node):
        self.node = node

    def find_all_in_node(self, tag):
        return self.node.findall(".//{}".format(tag), namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes_in_node(self, tag, attribute):
        elements = self.find_all_in_node(tag)
        return {element.attrib[attribute]: element for element in elements}


class NumberBox(object):
    NAMESPACE_MAP = {
        "html": "http://www.w3.org/1999/xhtml",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xmlns": "http://www.w3.org/2000/xmlns/",
        None: "http://www.w3.org/2000/svg",
    }

    OPERATOR_DETECTION = ["+", "-", "x", "*", "/", "×", "÷"]
    MULTIPLICATION_DETECTION = ["x", "*", "×"]
    DIVISION_DETECTION = ["/", "÷"]
    OPERATORS = ["+", "-", "×", "÷"]

    # Note: To shrink use matrix(0.57512451,0,0,0.57512451,14.269629,109.69556)

    def __init__(self, value=None):
        parser = ET.XMLParser(recover=True)
        self.box_node = SvgNode(ET.fromstring(BOX_TEMPLATE, parser))

        groups = self.box_node.find_all_in_node("g")
        self.group = groups[0]

        texts = self.box_node.find_all_in_node("text")
        self.text = texts[0]

        tspans = self.box_node.find_all_in_node("tspan")
        self.tspan = tspans[0]

        rects = self.box_node.find_all_in_node("rect")
        self.rect = rects[0]

        self.tspan.text = str(value) if value else ""
        if value in self.OPERATOR_DETECTION:
            self._handle_operators(value)

    def _handle_operators(self, value):
        if self.text is None or self.tspan is None:
            return

        self.text.attrib["y"] = "4.2380905"
        self.tspan.attrib["y"] = "4.2380905"
        self.text.attrib["x"] = "1.5323327"
        self.tspan.attrib["x"] = "1.5323327"

        if value == "-":
            self.text.attrib["x"] = "2.0614994"
            self.tspan.attrib["x"] = "2.0614994"
        elif value in self.MULTIPLICATION_DETECTION:
            self.tspan.text = self.OPERATORS[2]
        elif value in self.DIVISION_DETECTION:
            self.tspan.text = self.OPERATORS[3]

    def _remove_text(self):
        self.group.remove(self.text)
        self.text = None
        self.tspan = None


class ExerciseBox(object):
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
        number_box = NumberBox(0)

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
                new_box = NumberBox(value_string[i])

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


class AddSubTemplate:
    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"
    TITLE_ID = "Title"

    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"

    def __init__(self):
        self.svg = SVGFile()

        text_elements = self.svg.find_all_elements_by_attributes("text", "id")

        self.title_element = text_elements[self.TITLE_ID]

        title_tspan_elements = self.svg.all_spans_in_text(self.title_element)
        self.title_tspan_elements = {
            element.attrib["id"]: element for element in title_tspan_elements
        }

        self.drawing_area_group = self.svg.find_all_elements_by_attributes(
            "g", "id"
        ).get("drawingArea")

        self.drawing_area = self.svg.find_all_elements_by_attributes_in_node(
            self.drawing_area_group, "rect", "id"
        ).get("drawingAreaRect")

    def create_new(self, algorithm, filename_addsub):
        operator_string = self._get_operator_string(algorithm.operations)
        self.title_tspan_elements[
            self.CONFIG_SPAN
        ].text = "Operators: {} - Max Num: {} - Seed: {}".format(
            operator_string, algorithm.max_value, algorithm.seed
        )

        exercises = []
        exercise_nodes = []
        for operator, values in algorithm.result:
            exercise = ExerciseBox(operator, values)
            svg_node = exercise.generateBox()

            exercises.append(exercise)
            exercise_nodes.append(svg_node)

        self._distribute_exercises(
            exercise_nodes,
            self.drawing_area,
            self.drawing_area_group,
        )

        self.svg.write(filename_addsub)

    def _distribute_exercises(self, exercise_list, drawing_area, drawing_area_group):
        drawing_box_origin_x = float(drawing_area.attrib["x"])
        drawing_box_origin_y = float(drawing_area.attrib["y"])
        drawing_box_width = float(drawing_area.attrib["width"])
        drawing_box_height = float(drawing_area.attrib["height"])

        current_x, current_y = drawing_box_origin_x, drawing_box_origin_y
        row_spacing = 10
        row_height = 0
        row_elements = []

        for exercise in exercise_list:
            bbox = self._calculate_group_dimensions(exercise)
            g_width = float(bbox["width"])
            g_height = float(bbox["height"])

            # Move to next row if width exceeds limit
            if current_x + g_width > drawing_box_origin_x + drawing_box_width:
                # Calculate dynamic padding
                total_width = sum(
                    float(self._calculate_group_dimensions(e)["width"])
                    for e in row_elements
                )
                space_remaining = drawing_box_width - total_width
                padding = (
                    space_remaining / (len(row_elements) - 1)
                    if len(row_elements) > 1
                    else 0
                )

                # Adjust positions in the row
                x_offset = drawing_box_origin_x
                for elem in row_elements:
                    bbox = self._calculate_group_dimensions(elem)
                    elem.attrib["transform"] = f"translate({x_offset},{current_y})"
                    x_offset += bbox["width"] + padding

                    drawing_area_group.append(elem)

                # Reset for new row
                current_x = drawing_box_origin_x
                current_y += row_height + row_spacing
                row_height = 0
                row_elements = []

            # If exceeds drawing height, stop placing
            if current_y + g_height > drawing_box_origin_y + drawing_box_height:
                break

            # Store element in row list
            row_elements.append(exercise)

            # Update cursor position
            current_x += g_width
            row_height = max(row_height, g_height)

        # Final row adjustment
        if row_elements:
            total_width = sum(
                float(self._calculate_group_dimensions(e)["width"])
                for e in row_elements
            )
            space_remaining = drawing_box_width - total_width
            padding = (
                space_remaining / (len(row_elements) - 1)
                if len(row_elements) > 1
                else 0
            )

            x_offset = drawing_box_origin_x
            for elem in row_elements:
                bbox = self._calculate_group_dimensions(elem)
                elem.attrib["transform"] = f"translate({x_offset},{current_y})"
                x_offset += bbox["width"] + padding

                drawing_area_group.append(elem)

    def _parse_transform(self, transform):
        """Extracts translation values from the transform attribute."""
        if transform:
            match = re.search(r"translate\(([-\d.]+)[, ]*([-\d.]+)?\)", transform)
            if match:
                x = float(match.group(1))
                y = float(match.group(2)) if match.group(2) else 0
                return x, y
        return 0, 0

    def _calculate_group_dimensions(self, group):
        """
        Recursively calculates the bounding box dimensions of a group element,
        considering nested groups and child elements.

        :param group: lxml element representing the <g> group node.
        :return: Dictionary with 'width' and 'height' of the group.
        """
        if not len(group):
            return {"width": 0, "height": 0}

        min_x, min_y, max_x, max_y = (
            float("inf"),
            float("inf"),
            float("-inf"),
            float("-inf"),
        )
        group_x, group_y = self._parse_transform(group.get("transform"))

        for element in group.iterchildren():
            if element.tag.endswith("g"):
                dims = self._calculate_group_dimensions(element)
                child_x, child_y = self._parse_transform(
                    element.attrib.get("transform")
                )
                x = group_x + child_x
                y = group_y + child_y
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + dims["width"])
                max_y = max(max_y, y + dims["height"])
            else:
                x = group_x + float(element.attrib.get("x", 0))
                y = group_y + float(element.attrib.get("y", 0))
                width = float(element.attrib.get("width", 0))
                height = float(element.attrib.get("height", 0))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + width)
                max_y = max(max_y, y + height)

        return {
            "width": max_x - min_x if max_x > min_x else 0,
            "height": max_y - min_y if max_y > min_y else 0,
        }

    def _set_text(self, element, text):
        element[0].text = text

    def _get_operator_string(self, operators):
        result = ""
        for operator in operators:
            if operator == Operator.ADDITION:
                result = result + "+"
            elif operator == Operator.SUBTRACTION:
                result = result + "-"
            elif operator == Operator.MULTIPLICATION:
                result = result + "*"
            elif operator == Operator.DIVISION:
                result = result + "/"
        return result


class addsubAlgorithm:
    def __init__(
        self,
        operator_list,
        min_value,
        max_value,
        num_exercises,
        num_rows_per_exercise,
        rand_seed,
    ):
        self.operations = operator_list
        self.min_value = min_value
        self.max_value = max_value
        self.num_exercises = num_exercises
        self.num_rows_per_exercise = num_rows_per_exercise
        self.seed = rand_seed

        seed(rand_seed)

    def build_addsub(self):
        results = []

        start = randrange(self.max_value)

        for i in range(self.num_exercises):
            operator = choice(self.operations)

            counter = 0
            while True:
                counter += 1
                if counter > 10:
                    raise RuntimeError("addsub has no solution. Infinite loop.")

                values = [
                    randrange(self.min_value, self.max_value)
                    for i in range(self.num_rows_per_exercise)
                ]

                if operator == Operator.SUBTRACTION:
                    # swap out the max value and move it to the beginning
                    max_value_index = values.index(max(values))
                    values[0], values[max_value_index] = (
                        values[max_value_index],
                        values[0],
                    )

                if self.choice_criterium(operator, values):
                    print("CHOICE: ", operator, values)
                    results.append((operator, values))
                    break
                else:
                    print(operator, values)

        self.result = results

    def choice_criterium(self, operator, values):
        if operator == Operator.ADDITION:
            if sum(values) > self.max_value:
                return False

        if operator == Operator.SUBTRACTION:
            value_copy = deepcopy(values)
            value_copy[0] = -1 * value_copy[0]
            if sum([-1 * v for v in value_copy]) < 0:
                return False

        return True


def main():
    template = AddSubTemplate()
    algorithm = addsubAlgorithm(
        OPERATORS, MIN_VALUE, MAX_VALUE, NUM_EXERCISES, NUM_ROWS_PER_EXERCISE, SEED
    )
    algorithm.build_addsub()
    template.create_new(algorithm, "test.svg")

    # print(template.value_elements)
    # print(template.operator_elements)
    # print(template.title_element)


if __name__ == "__main__":
    main()
