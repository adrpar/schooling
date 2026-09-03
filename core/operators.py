from enum import Enum

__all__ = ["Operator"]


class Operator(Enum):
    """Arithmetic operator used across all exercise types."""

    ADDITION = 1
    SUBTRACTION = 2
    MULTIPLICATION = 3
    DIVISION = 4
