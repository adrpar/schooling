import logging
from random import Random
from typing import Optional

from core.operators import Operator

__all__ = ["AddSubAlgorithm"]

logger = logging.getLogger(__name__)


class AddSubAlgorithm:
    def __init__(
        self,
        operator_list: list[Operator],
        min_value: int,
        max_value: int,
        num_exercises: int,
        num_rows_per_exercise: int,
        rand_seed: Optional[int] = None,
    ) -> None:
        self.operations = operator_list
        self.min_value = min_value
        self.max_value = max_value
        self.num_exercises = num_exercises
        self.num_rows_per_exercise = num_rows_per_exercise
        self.seed = rand_seed
        self.rng = Random(rand_seed)
        self.result: list[tuple[Operator, list[int]]] = []

    def build_addsub(self) -> None:
        results: list[tuple[Operator, list[int]]] = []

        for _ in range(self.num_exercises):
            operator = self.rng.choice(self.operations)

            counter = 0
            while True:
                counter += 1
                if counter > 100:
                    raise RuntimeError("addsub has no solution. Infinite loop.")

                values = [
                    self.rng.randrange(
                        self.min_value, max(self.min_value + 1, self.max_value)
                    )
                    for _ in range(self.num_rows_per_exercise)
                ]

                if operator == Operator.SUBTRACTION:
                    # swap out the max value and move it to the beginning
                    max_value_index = values.index(max(values))
                    values[0], values[max_value_index] = (
                        values[max_value_index],
                        values[0],
                    )

                if self.choice_criterium(operator, values):
                    logger.debug("CHOICE: %s %s", operator, values)
                    results.append((operator, values))
                    break
                else:
                    logger.debug("Rejected: %s %s", operator, values)

        self.result = results

    def choice_criterium(self, operator: Operator, values: list[int]) -> bool:
        if operator == Operator.ADDITION:
            if sum(values) > self.max_value:
                return False

        if operator == Operator.SUBTRACTION:
            if values[0] - sum(values[1:]) < 0:
                return False

        return True
