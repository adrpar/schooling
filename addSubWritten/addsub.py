from copy import deepcopy
from enum import Enum
from random import seed, randrange, choice
from svg.svg_handler import SVGFile
from svg.number_paper.written_calc_exercise_box import WrittenCalcExerciseBox
from svg.svg_groups import calculate_group_dimensions, distribute_groups_in_drawing_area

import lxml.etree as ET

import re

BOX_STROKE_WIDTH = 0.223193


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


class AddSubTemplate:
    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"
    TITLE_ID = "Title"

    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"

    def __init__(self):
        self.svg = SVGFile("addSubWritten/drawing.svg")

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
            exercise = WrittenCalcExerciseBox(operator, values)  # Updated reference
            svg_node = exercise.generateBox()

            exercises.append(exercise)
            exercise_nodes.append(svg_node)

        distribute_groups_in_drawing_area(
            exercise_nodes,
            self.drawing_area,
            self.drawing_area_group,
        )

        self.svg.write(filename_addsub)

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
