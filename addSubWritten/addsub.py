from copy import deepcopy
from enum import Enum
from random import seed, randrange, choice

from addSubWritten.algorithm import AddSubAlgorithm, Operator
from addSubWritten.template import AddSubTemplate
from svg.svg_handler import SVGFile
from svg.number_paper.written_calc_exercise_box import WrittenCalcExerciseBox

import lxml.etree as ET

import re

BOX_STROKE_WIDTH = 0.223193

# CONFIG SECTION

OPERATORS = [
    Operator.ADDITION,
    Operator.SUBTRACTION,
    # Operator.MULTIPLICATION,
    # Operator.DIVISION,
]
MIN_VALUE = 1
MAX_VALUE = 9999
SEED = 7874
NUM_EXERCISES = 30
NUM_ROWS_PER_EXERCISE = 2


def main():
    template = AddSubTemplate()
    algorithm = AddSubAlgorithm(
        OPERATORS, MIN_VALUE, MAX_VALUE, NUM_EXERCISES, NUM_ROWS_PER_EXERCISE, SEED
    )
    algorithm.build_addsub()
    template.create_new(algorithm, "test.svg")

    # print(template.value_elements)
    # print(template.operator_elements)
    # print(template.title_element)


if __name__ == "__main__":
    main()
