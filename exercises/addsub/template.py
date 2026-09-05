from pathlib import Path
from typing import Any, Optional

from core.operators import Operator
from exercises.utils import operator_to_string
from svg.number_paper.written_calc_exercise_box import WrittenCalcExerciseBox
from svg.svg_groups import distribute_groups_in_drawing_area
from svg.template import Template, Element, validate_template

_TEMPLATE = Path(__file__).parent / "drawing.svg"


class AddSubTemplate:
    """Generic SVG template for add/sub exercises using Template class."""
    
    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"
    TITLE_ID = "Title"

    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"

    def __init__(self):
        self.template = Template(str(_TEMPLATE))
        self.title_element = self.template.get_element(self.TITLE_ID)

        title_tspan_elements = self.template.find_all_by_tag("tspan", self.title_element)
        self.title_tspan_elements = {
            element.get_attribute("id"): element for element in title_tspan_elements
        }

        self.drawing_area_group = self.template.get_element_by_id("drawingArea")
        self.drawing_area = self.template.find_by_tag_and_attribute(
            self.drawing_area_group, "rect", "id"
        )

    def create_new(self, algorithm, filename_addsub):
        op_string = operator_to_string(algorithm.operations)
        self.title_tspan_elements[self.CONFIG_SPAN].set_text(
            "Operators: {} - Max Num: {} - Seed: {}".format(
                op_string, algorithm.max_value, algorithm.seed
            )
        )

        exercises = []
        exercise_nodes = []
        for operator, values in algorithm.result:
            exercise = WrittenCalcExerciseBox(operator, values)
            svg_node = exercise.generateBox()
            element = Element(svg_node)

            exercises.append(exercise)
            exercise_nodes.append(element)

        distribute_groups_in_drawing_area(
            exercise_nodes,
            self.drawing_area,
            self.drawing_area_group,
        )

        self.template.write(filename_addsub)

    def _set_text(self, element, text):
        element.set_text(text)
