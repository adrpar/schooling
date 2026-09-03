import logging
from random import choice, randrange, seed

from core.operators import Operator

__all__ = ["RallyAlgorithm"]

logger = logging.getLogger(__name__)


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
                    logger.debug(
                        "CHOICE: %s %s %s → %s",
                        results[-1][2],
                        operator,
                        value,
                        curr_result,
                    )
                    results.append((operator, value, curr_result))
                    break
                else:
                    logger.debug("Rejected: %s %s → %s", operator, value, curr_result)

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
