from core.operators import Operator
from exercises.addsub.algorithm import AddSubAlgorithm
from exercises.addsub.template import AddSubTemplate

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


if __name__ == "__main__":
    main()
