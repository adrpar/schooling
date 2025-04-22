from copy import deepcopy
from enum import Enum
from random import choice, randrange, seed

__all__ = ["AddSubAlgorithm", "Operator"]

class Operator(Enum):
    ADDITION = 1
    SUBTRACTION = 2
    MULTIPLICATION = 3
    DIVISION = 4


class AddSubAlgorithm:
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
