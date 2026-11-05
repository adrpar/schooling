"""
exercises.mathrally — Math Rally chain-calculation exercise.

Provides:
- `RallyAlgorithm`: Generates a sequence of arithmetic operations forming a continuous calculation trail.
- `RallyTemplate`: Injects step values, operators, and solutions into pre-drawn SVG rally templates.
- `Operator`: Arithmetic operator enum (`ADD`, `SUBTRACT`, `MULTIPLY`, `DIVIDE`).
"""

from core.operators import Operator
from .algorithm import RallyAlgorithm
from .template import RallyTemplate

__all__ = ["Operator", "RallyAlgorithm", "RallyTemplate"]
