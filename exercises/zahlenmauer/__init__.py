"""
exercises.zahlenmauer — Additive number pyramids ("Zahlenmauer").

Provides:
- `Difficulty`: Enum for puzzle challenge level (`EASY`, `MEDIUM`, `HARD`).
- `ZahlenmauerAlgorithm`: Generates valid, solvable number pyramids with difficulty-driven brick masking.
- `ZahlenmauerPuzzle`: Data structure holding the full solution pyramid and masked visible bricks.
- `ZahlenmauerSolver`: Deduction-based solver verifying unambiguous solvability.
- `ZahlenmauerTemplate`: Programmatically constructs staggered brickwork SVG elements.
- `get_optimal_pyramid_count`: Calculates optimal pyramid packing count for standard A4 pages.
"""

from exercises.zahlenmauer.algorithm import (
    ZahlenmauerAlgorithm,
    ZahlenmauerPuzzle,
    ZahlenmauerSolver,
    get_optimal_pyramid_count,
)
from exercises.zahlenmauer.difficulty import Difficulty
from exercises.zahlenmauer.template import ZahlenmauerTemplate

__all__ = [
    "Difficulty",
    "ZahlenmauerAlgorithm",
    "ZahlenmauerPuzzle",
    "ZahlenmauerSolver",
    "ZahlenmauerTemplate",
    "get_optimal_pyramid_count",
]
