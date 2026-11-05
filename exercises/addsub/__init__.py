"""
exercises.addsub — Written arithmetic (column-form addition & subtraction).

Provides:
- `AddSubAlgorithm`: Generates column arithmetic exercises with valid non-negative results.
- `AddSubTemplate`: Renders exercises on simulated grid (number) paper.
- `Operator`: Arithmetic operator enum (`ADD`, `SUBTRACT`).
"""

from core.operators import Operator
from .algorithm import AddSubAlgorithm
from .template import AddSubTemplate

__all__ = ["AddSubAlgorithm", "AddSubTemplate", "Operator"]
