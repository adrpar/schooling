from pathlib import Path
from typing import Optional, Union

from core.operators import Operator
from exercises.utils import operator_to_string
from svg.canvas_template import (
    CanvasExerciseTemplate,
    calc_adaptive_font_size,
    center_text_in_circle,
    center_text_in_rect,
    highlight_solution_box,
)
from svg.styles import (
    COLOR_SOLUTION,
    COLOR_TEXT_PRIMARY,
    FONT_FAMILY,
)

# Fallback dimensions for Math Rally SVG value box elements (from Inkscape template Rally1.svg).
# These coordinates define the default rectangle bounding box and circle center used when
# individual elements in the template do not declare explicit x/y/width/height/cx/cy attributes.
# - RALLY_VALUE_RECT_FALLBACK_BOUNDS: (x=33.76, y=57.66, width=20.75, height=12.74 in mm),
#   corresponding to the dimensions of the initial value.0 box.
# - RALLY_OPERATOR_CIRCLE_FALLBACK_CENTER: (cx=144.28, cy=126.31 in mm),
#   corresponding to the center point of the first operator circle.
RALLY_VALUE_RECT_FALLBACK_BOUNDS = (33.757515, 57.658085, 20.754112, 12.74199)
RALLY_OPERATOR_CIRCLE_FALLBACK_CENTER = (144.27673, 126.3138)


class RallyTemplate(CanvasExerciseTemplate):
    """
    Template for generating Math Rally winding arithmetic path exercise sheets.
    Inherits from CanvasExerciseTemplate for standardized header, footer, and styling.
    """

    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"

    def __init__(self, file_name: Union[str, Path]):
        self.file_name = file_name
        super().__init__(file_name)
        # Retain backward-compatible references
        self.svg = self.doc
        self.title_tspan_elements = self.title_tspans

        text_elements = self.doc.find_all_with_attr("text", "id")

        self.value_elements = {
            key: element
            for key, element in text_elements.items()
            if self.VALUE_ID_PREFIX in key
        }
        self.operator_elements = {
            key: element
            for key, element in text_elements.items()
            if self.OPERATOR_TEXT_ID_PREFIX in key
        }

        self._validate_assumptions()

        self.num_operators = len(self.operator_elements.keys())
        self.num_value_elements = len(self.value_elements.keys())

    def _validate_assumptions(self):
        operator_ids = [int(key.split(".")[1]) for key in self.operator_elements.keys()]
        operator_ids = sorted(operator_ids)
        if not all([i == id for i, id in enumerate(operator_ids)]):
            raise ValueError("Operator ids are not consecutive")

        value_ids = [int(key.split(".")[1]) for key in self.value_elements.keys()]
        value_ids = sorted(value_ids)
        if not all([i == id for i, id in enumerate(value_ids)]):
            raise ValueError("Value ids are not consecutive")

        num_operators = len(self.operator_elements.keys())
        num_value_elements = len(self.value_elements.keys())

        if (num_value_elements - num_operators) != 1:
            raise ValueError(
                "Template has not one more value field than operations fields"
            )

        if not all(
            [
                element in ["TitleSpan", "ConfigSpan"]
                for element in self.title_tspan_elements.keys()
            ]
        ):
            raise ValueError("Title does not contain expected tspans")

    def _format_value_element(
        self, text_elem, val_text: str, is_solution: bool = False, is_start: bool = False
    ):
        """Cleanly center and style value boxes using generic SVG centering and font scaling."""
        if len(text_elem) > 0:
            text_elem[0].text = str(val_text) if val_text else ""
        else:
            text_elem.text = str(val_text) if val_text else ""

        raw_text = text_elem.raw_element if hasattr(text_elem, "raw_element") else text_elem
        raw_parent = raw_text.getparent()
        rect = (
            raw_parent.find("{http://www.w3.org/2000/svg}rect")
            if raw_parent is not None
            else None
        )

        center_text_in_rect(text_elem, rect_elem=rect, fallback_bounds=RALLY_VALUE_RECT_FALLBACK_BOUNDS)

        fsize = calc_adaptive_font_size(
            val_text,
            max_font_size=6.0,
            min_font_size=3.8,
            length_thresholds=[(1, 6.0), (2, 5.5), (3, 4.5)],
        )
        is_solved_val = is_solution and not is_start and bool(val_text)
        fill_color = COLOR_SOLUTION if is_solved_val else COLOR_TEXT_PRIMARY

        style = (
            f"font-family:{FONT_FAMILY};font-weight:bold;font-size:{fsize};"
            f"fill:{fill_color};stroke:none;text-anchor:middle;dominant-baseline:central;"
        )
        text_elem.attrib["style"] = style
        for child in text_elem:
            child.attrib["style"] = style

        if is_solved_val and rect is not None:
            highlight_solution_box(rect, text_elem)

    def _format_operator_element(self, text_elem, op_text: str):
        """Cleanly center and style operator circles using generic circle centering."""
        if len(text_elem) > 0:
            text_elem[0].text = str(op_text)
        else:
            text_elem.text = str(op_text)

        raw_text = text_elem.raw_element if hasattr(text_elem, "raw_element") else text_elem
        raw_parent = raw_text.getparent()
        circle = None
        prev = raw_text.getprevious()
        if prev is not None and prev.tag.endswith("circle"):
            circle = prev
        elif (
            raw_parent is not None
            and raw_parent.attrib.get("id") != "layer1"
            and not raw_parent.tag.endswith("svg")
        ):
            circle = raw_parent.find("{http://www.w3.org/2000/svg}circle")

        center_text_in_circle(text_elem, circle_elem=circle, fallback_center=RALLY_OPERATOR_CIRCLE_FALLBACK_CENTER)

        fsize = calc_adaptive_font_size(
            op_text,
            max_font_size=4.5,
            min_font_size=3.5,
            length_thresholds=[(2, 4.5), (3, 4.1)],
        )

        style = (
            f"font-family:{FONT_FAMILY};font-weight:bold;font-size:{fsize};"
            f"fill:{COLOR_TEXT_PRIMARY};stroke:none;text-anchor:middle;dominant-baseline:central;"
        )
        text_elem.attrib["style"] = style
        for child in text_elem:
            child.attrib["style"] = style

    def create_new_rally(self, algorithm_results, filename_rally, filename_solution):
        solution_copy = RallyTemplate(self.file_name)
        rally_copy = RallyTemplate(self.file_name)

        op_string = operator_to_string(algorithm_results.operations)
        config_text = f"Operators: {op_string} - Max Num: {algorithm_results.max_value} - Seed: {algorithm_results.seed}"

        # Standardized headers and footers from CanvasExerciseTemplate
        rally_copy.set_header("Math Rally", config_text)
        rally_copy.set_footer(visible=True)

        solution_copy.set_header("Math Rally — Lösung", config_text)
        solution_copy.set_footer(visible=False)

        for i, element in enumerate(algorithm_results.result):
            if i == 0:
                val = str(element[2])
                self._format_value_element(
                    solution_copy.value_elements["value.0"],
                    val,
                    is_solution=True,
                    is_start=True,
                )
                self._format_value_element(
                    rally_copy.value_elements["value.0"],
                    val,
                    is_solution=False,
                    is_start=True,
                )
            else:
                val = str(element[2])
                self._format_value_element(
                    solution_copy.value_elements[f"value.{i}"],
                    val,
                    is_solution=True,
                    is_start=False,
                )
                self._format_value_element(
                    rally_copy.value_elements[f"value.{i}"],
                    "",
                    is_solution=False,
                    is_start=False,
                )

                op_symbol = operator_to_string([element[0]])
                operator_text = f"{op_symbol}{element[1]}"
                self._format_operator_element(
                    solution_copy.operator_elements[f"operatorText.{i - 1}"],
                    operator_text,
                )
                self._format_operator_element(
                    rally_copy.operator_elements[f"operatorText.{i - 1}"],
                    operator_text,
                )

        solution_copy.write(filename_solution)
        rally_copy.write(filename_rally)
