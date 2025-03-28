from copy import deepcopy
from enum import Enum
from random import seed, randrange, choice
from svg.svg_handler import SVGFile  # Import the SVGFile class from the new module

import lxml.etree as ET


TEMPLATE_PATH = "./img"
TEMPLATE_NAME = "Rally1.svg"


class Operator(Enum):
    ADDITION = 1
    SUBTRACTION = 2
    MULTIPLICATION = 3
    DIVISION = 4


OPERATORS = [
    Operator.ADDITION,
    Operator.SUBTRACTION,
    Operator.MULTIPLICATION,
    Operator.DIVISION,
]
MIN_VALUE = 1
MAX_VALUE = 100
SEED = 7875


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


class RallyAlgorithm:
    def __init__(self, operator_list, min_value, max_value, num_operators, rand_seed):
        self.operations = operator_list
        self.min_value = min_value
        self.max_value = max_value
        self.num_operators = num_operators
        self.seed = rand_seed

        seed(rand_seed)

    def build_rally(self):
        results = []

        start = randrange(self.max_value)

        results.append((None, None, start))

        for i in range(self.num_operators):
            counter = 0
            while True:
                counter += 1
                if counter > 10:
                    raise RuntimeError("Rally has no solution. Infinite loop.")

                operator = choice(self.operations)
                value = randrange(self.min_value, self.max_value)

                curr_result = None
                if operator == Operator.ADDITION:
                    curr_result = results[-1][2] + value
                elif operator == Operator.SUBTRACTION:
                    curr_result = results[-1][2] - value
                elif operator == Operator.MULTIPLICATION:
                    value = int(value / 10.0)
                    curr_result = results[-1][2] * value
                elif operator == Operator.DIVISION:
                    value = int(value / 10.0)
                    if value == 0 or int(results[-1][2]) % value != 0:
                        continue

                    curr_result = results[-1][2] / value

                if self.choice_criterium(curr_result, operator, value, results):
                    print("CHOICE: ", results[-1][2], operator, value, curr_result)
                    results.append((operator, value, curr_result))
                    break
                else:
                    print(operator, value, curr_result)

        self.result = results

    def choice_criterium(self, curr_result, operator, value, results):
        if curr_result < self.min_value:
            return False
        if curr_result > self.max_value:
            return False
        # checking whether the next operation is cancelling the last one
        operator_check = set([operator, results[-1][0]])
        if operator_check == set(
            [Operator.ADDITION, Operator.SUBTRACTION]
        ) or operator_check == set([Operator.MULTIPLICATION, Operator.DIVISION]):
            if value == results[-1][1]:
                return False

        return True
