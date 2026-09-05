"""Shared utilities for exercise template rendering."""

from core.operators import Operator

__all__ = ["operator_to_string"]

_OPERATOR_SYMBOLS = {
    Operator.ADDITION: "+",
    Operator.SUBTRACTION: "-",
    Operator.MULTIPLICATION: "*",
    Operator.DIVISION: "/",
}


def operator_to_string(operators: list[Operator]) -> str:
    """Return a compact symbol string for a list of Operators (e.g. [+, -] → '+-')."""
    return "".join(_OPERATOR_SYMBOLS[op] for op in operators)
