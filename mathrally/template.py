from addSubWritten.algorithm import Operator
from svg.svg_handler import SVGFile


class RallyTemplate:
    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"
    TITLE_ID = "Title"

    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"

    def __init__(self, file_name):
        self.file_name = file_name
        self.svg = SVGFile(file_name)

        text_elements = self.svg.find_all_elements_by_attributes("text", "id")

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
        self.title_element = text_elements[self.TITLE_ID]

        title_tspan_elements = self.svg.all_spans_in_text(self.title_element)
        self.title_tspan_elements = {
            element.attrib["id"]: element for element in title_tspan_elements
        }
        self._validate_assumptions()

        self.num_operators = len(self.operator_elements.keys())
        self.num_value_elements = len(self.value_elements.keys())

    def _validate_assumptions(self):
        operator_ids = [int(key.split(".")[1]) for key in self.operator_elements.keys()]
        operator_ids = sorted(operator_ids)
        if not all([i == id for i, id in enumerate(operator_ids)]):
            print(operator_ids)
            raise ValueError("Operator ids are not consecutive")

        value_ids = [int(key.split(".")[1]) for key in self.value_elements.keys()]
        value_ids = sorted(value_ids)
        if not all([i == id for i, id in enumerate(value_ids)]):
            print(value_ids)
            raise ValueError("Value ids are not consecutive")

        num_operators = len(self.operator_elements.keys())
        num_value_elements = len(self.value_elements.keys())

        if (num_value_elements - num_operators) != 1:
            print(num_value_elements, num_operators)
            raise ValueError(
                "Template has not one more value field than operations fields"
            )

        if not all(
            [
                element in ["TitleSpan", "ConfigSpan"]
                for element in self.title_tspan_elements.keys()
            ]
        ):
            print(self.title_tspan_elements)
            raise ValueError("Title does not contain expected tspans")

    def create_new_rally(self, algorithm_results, filename_rally, filename_solution):
        solution_copy = RallyTemplate(self.file_name)
        rally_copy = RallyTemplate(self.file_name)

        operator_string = self._get_operator_string(algorithm_results.operations)
        solution_copy.title_tspan_elements[
            self.CONFIG_SPAN
        ].text = "Operators: {} - Max Num: {} - Seed: {}".format(
            operator_string, algorithm_results.max_value, algorithm_results.seed
        )
        rally_copy.title_tspan_elements[
            self.CONFIG_SPAN
        ].text = "Operators: {} - Max Num: {} - Seed: {}".format(
            operator_string, algorithm_results.max_value, algorithm_results.seed
        )

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
                    self._get_operator_string([element[0]]), element[1]
                )
                self._set_text(
                    solution_copy.operator_elements["operatorText.{}".format(i - 1)],
                    operator_text,
                )
                self._set_text(
                    rally_copy.operator_elements["operatorText.{}".format(i - 1)],
                    operator_text,
                )

        solution_copy.svg.write(filename_solution)
        rally_copy.svg.write(filename_rally)

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