from pathlib import Path
from typing import Any, Optional

from core.operators import Operator
from exercises.utils import operator_to_string
from svg.template import Template, Element, validate_template

_TEMPLATE = Path(__file__).parent / "template" / "mathrally.svg"


class RallyTemplate:
    """Generic SVG template for math rally exercises using Template class."""
    
    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"
    TITLE_ID = "Title"

    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"

    def __init__(self, file_name: Optional[str] = None):
        self.template = Template(file_name or str(_TEMPLATE))
        self.title_element = self.template.get_element(self.TITLE_ID)

        text_elements = self.template.find_all_by_tag("text", self.title_element)
        self.title_tspan_elements = {
            element.get_attribute("id"): element for element in text_elements
        }

        self._validate_assumptions()

        self.num_operators = len(self.title_tspan_elements) - 1
        self.num_value_elements = len(self.title_tspan_elements)

    def _validate_assumptions(self):
        validate_template(self.template)
        raise NotImplementedError("Validation logic to be implemented")

    def create_new_rally(self, algorithm_results, filename_rally: str, filename_solution: str):
        solution_copy = RallyTemplate(str(_TEMPLATE))
        rally_copy = RallyTemplate(str(_TEMPLATE))

        op_string = operator_to_string(algorithm_results.operations)
        config_text = "Operators: {} - Max Num: {} - Seed: {}".format(
            op_string, algorithm_results.max_value, algorithm_results.seed
        )
        solution_copy.title_tspan_elements[self.CONFIG_SPAN].set_text(config_text)
        rally_copy.title_tspan_elements[self.CONFIG_SPAN].set_text(config_text)

        for i, element in enumerate(algorithm_results.result):
            if i == 0:
                self._set_text(
                    solution_copy.value_elements["value.0"], "{}".format(element[2])
                )
                self._set_text(
                    rally_copy.value_elements["value.0"], "{}".format(element[2])
                )
            else:
                self._set_text(
                    solution_copy.value_elements["value.{}".format(i)],
                    "{}".format(element[2]),
                )
                self._set_text(rally_copy.value_elements["value.{}".format(i)], "")
                operator_text = "{}{}".format(
                    operator_to_string([element[0]]), element[1]
                )
                self._set_text(
                    solution_copy.operator_elements["operatorText.{}".format(i - 1)],
                    operator_text,
                )
                self._set_text(
                    rally_copy.operator_elements["operatorText.{}".format(i - 1)],
                    operator_text,
                )

        solution_copy.template.write(filename_solution)
        rally_copy.template.write(filename_rally)

    def _set_text(self, element: Element, text: str):
        element.set_text(text)
