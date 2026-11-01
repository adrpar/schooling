import logging
from random import Random
from typing import NamedTuple, Optional

from core.operators import Operator

__all__ = ["RallyAlgorithm", "RallyStep"]

logger = logging.getLogger(__name__)


class RallyStep(NamedTuple):
    operator: Optional[Operator]
    operand: Optional[int]
    result: int


class RallyAlgorithm:
    def __init__(self, operator_list, min_value, max_value, num_operators, rand_seed):
        self.operations = operator_list
        self.min_value = min_value
        self.max_value = max_value
        self.num_operators = num_operators
        self.seed = rand_seed
        self.rng = Random(rand_seed)

    def build_rally(self):
        results: list[RallyStep] = []

        start = self.rng.randrange(self.min_value, max(self.min_value + 1, self.max_value))
        results.append(RallyStep(None, None, start))

        for i in range(self.num_operators):
            counter = 0
            while True:
                counter += 1
                if counter > 100:
                    raise RuntimeError("Rally has no solution. Infinite loop.")

                operator = self.rng.choice(self.operations)
                curr_val = results[-1].result

                curr_result = None
                value = None

                if operator == Operator.ADDITION:
                    value = self.rng.randrange(self.min_value, max(self.min_value + 1, self.max_value))
                    curr_result = curr_val + value
                elif operator == Operator.SUBTRACTION:
                    value = self.rng.randrange(self.min_value, max(self.min_value + 1, self.max_value))
                    curr_result = curr_val - value
                elif operator == Operator.MULTIPLICATION:
                    max_mult = min(10, max(2, self.max_value // max(1, curr_val)))
                    value = self.rng.randint(2, max(2, max_mult))
                    curr_result = curr_val * value
                elif operator == Operator.DIVISION:
                    divisors = [
                        d for d in range(2, 11)
                        if curr_val % d == 0 and (curr_val // d) >= self.min_value
                    ]
                    if not divisors:
                        continue
                    value = self.rng.choice(divisors)
                    curr_result = curr_val // value

                if self.choice_criterium(curr_result, operator, value, results):
                    logger.debug(
                        "CHOICE: %s %s %s → %s",
                        curr_val,
                        operator,
                        value,
                        curr_result,
                    )
                    results.append(RallyStep(operator, value, curr_result))
                    break
                else:
                    logger.debug("Rejected: %s %s → %s", operator, value, curr_result)

        self.result = results

    def choice_criterium(self, curr_result, operator, value, results):
        if curr_result is None or value is None:
            return False
        if curr_result < self.min_value:
            return False
        if curr_result > self.max_value:
            return False
        # checking whether the next operation is cancelling the last one
        last_op = results[-1][0]
        last_operand = results[-1][1]
        operator_check = set([operator, last_op])
        if operator_check == set(
            [Operator.ADDITION, Operator.SUBTRACTION]
        ) or operator_check == set([Operator.MULTIPLICATION, Operator.DIVISION]):
            if value == last_operand:
                return False

        return True
