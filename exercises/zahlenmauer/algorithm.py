import logging
import math
from random import Random
from typing import NamedTuple, Optional

from exercises.zahlenmauer.difficulty import Difficulty

__all__ = ["ZahlenmauerAlgorithm", "ZahlenmauerPuzzle", "ZahlenmauerSolver"]

logger = logging.getLogger(__name__)


class ZahlenmauerPuzzle(NamedTuple):
    base_size: int
    full_wall: list[list[int]]         # 2D grid: full_wall[row][col], row 0 is base
    masked_wall: list[list[Optional[int]]]  # 2D grid: None for hidden cells, int for visible
    difficulty: Difficulty


Cell = tuple[int, int]
DeductionStep = tuple[str, Cell]


class ZahlenmauerSolver:
    """
    Simulates step-by-step human student deduction on a Zahlenmauer.
    Verifies whether a puzzle configuration can be logically deduced without guessing.
    """

    @classmethod
    def solve(
        cls,
        base_size: int,
        known_cells: dict[Cell, int],
        allow_algebraic: bool = False,
    ) -> tuple[bool, list[DeductionStep]]:
        """
        Public entry point to simulate deduction on a Zahlenmauer.

        :param base_size: Number of bricks at the bottom row.
        :param known_cells: Map of (row, col) -> value of given clues.
        :param allow_algebraic: Whether to allow linear combination puzzle steps (e.g. 2b = Top - a - c).
        :return: (is_completely_solved, deduction_history)
        """
        solver = cls(base_size, known_cells, allow_algebraic=allow_algebraic)
        return solver.run()

    def __init__(
        self,
        base_size: int,
        known_cells: dict[Cell, int],
        allow_algebraic: bool = False,
    ):
        self.base_size = base_size
        self.grid = dict(known_cells)
        self.allow_algebraic = allow_algebraic
        self.history: list[DeductionStep] = []

    def run(self) -> tuple[bool, list[DeductionStep]]:
        """Executes deduction passes until solved, stalled, or contradiction found."""
        while True:
            # 1. Primary rule: Direct 2-out-of-3 triangular arithmetic (addition/subtraction)
            progress, is_valid = self._try_triad_deductions()
            if not is_valid:
                return False, self.history
            if progress:
                continue

            # 2. Secondary rule: Linear combinations across base cells (Knobelaufgabe for Hard)
            if self.allow_algebraic and self._try_algebraic_deductions():
                continue

            # No further deduction possible
            break

        total_cells = self.base_size * (self.base_size + 1) // 2
        is_solved = len(self.grid) == total_cells
        return is_solved, self.history

    def _iter_triads(self):
        """Yields (parent, left_child, right_child) for every brick triad in the wall."""
        for r in range(1, self.base_size):
            for c in range(self.base_size - r):
                yield (r, c), (r - 1, c), (r - 1, c + 1)

    def _try_triad_deductions(self) -> tuple[bool, bool]:
        """
        Scans all triads for direct 2-out-of-3 arithmetic inferences:
        - Upward: left + right -> parent
        - Downward: parent - left -> right
        - Downward: parent - right -> left
        Returns (progress_made, is_valid).
        """
        progress = False
        for parent, left, right in self._iter_triads():
            # Upward addition
            if left in self.grid and right in self.grid and parent not in self.grid:
                self.grid[parent] = self.grid[left] + self.grid[right]
                self.history.append(("add", parent))
                progress = True

            # Downward subtraction (missing right child)
            elif parent in self.grid and left in self.grid and right not in self.grid:
                val = self.grid[parent] - self.grid[left]
                if val < 0:
                    return False, False
                self.grid[right] = val
                self.history.append(("sub", right))
                progress = True

            # Downward subtraction (missing left child)
            elif parent in self.grid and right in self.grid and left not in self.grid:
                val = self.grid[parent] - self.grid[right]
                if val < 0:
                    return False, False
                self.grid[left] = val
                self.history.append(("sub", left))
                progress = True

        return progress, True

    def _try_algebraic_deductions(self) -> bool:
        """
        Attempts to solve for an unknown base cell by expressing a known higher
        brick as a linear combination of base bricks (using binomial coefficients).
        """
        for r in range(1, self.base_size):
            for c in range(self.base_size - r):
                cell = (r, c)
                if cell not in self.grid:
                    continue

                target_val = self.grid[cell]
                unknowns: list[tuple[Cell, int]] = []
                known_sum = 0

                for k in range(r + 1):
                    base_cell = (0, c + k)
                    coeff = math.comb(r, k)
                    if base_cell in self.grid:
                        known_sum += coeff * self.grid[base_cell]
                    else:
                        unknowns.append((base_cell, coeff))

                # If exactly one base cell is unknown in this subtree, deduce it directly
                if len(unknowns) == 1:
                    target_cell, coeff = unknowns[0]
                    remainder = target_val - known_sum
                    if remainder > 0 and remainder % coeff == 0:
                        self.grid[target_cell] = remainder // coeff
                        self.history.append(("algebraic", target_cell))
                        return True

        return False


def get_optimal_pyramid_count(base_size: int) -> int:
    """
    Returns the optimal number of pyramids that cleanly fit an A4 page
    for the given base size without overflow or truncation.
    """
    if base_size <= 6:
        return 6  # 2 columns x 3 rows
    elif base_size in (7, 8):
        return 2  # 1 column x 2 rows
    else:
        return 1  # 1 column x 1 row (large pyramid)


class ZahlenmauerAlgorithm:
    def __init__(
        self,
        base_size: int = 4,
        difficulty: Difficulty = Difficulty.MEDIUM,
        min_value: int = 1,
        max_value: int = 100,
        num_pyramids: Optional[int] = None,
        rand_seed: Optional[int] = None,
    ):
        if base_size < 3 or base_size > 10:
            raise ValueError(f"base_size must be between 3 and 10 (got {base_size})")

        min_apex = (2 ** (base_size - 1)) * min_value
        if min_apex > max_value:
            raise ValueError(
                f"max_value={max_value} is too small for base_size={base_size} with min_value={min_value}. "
                f"Minimum possible apex is {min_apex}."
            )

        self.base_size = base_size
        self.difficulty = difficulty
        self.min_value = min_value
        self.max_value = max_value
        self.num_pyramids = (
            num_pyramids
            if num_pyramids is not None
            else get_optimal_pyramid_count(base_size)
        )
        self.seed = rand_seed
        self.rng = Random(rand_seed)
        self.puzzles: list[ZahlenmauerPuzzle] = []

    def build(self) -> list[ZahlenmauerPuzzle]:
        self.puzzles = [self._generate_one_pyramid() for _ in range(self.num_pyramids)]
        return self.puzzles

    def _generate_one_pyramid(self) -> ZahlenmauerPuzzle:
        for _ in range(100):
            wall = self._generate_full_wall()
            masked = self._create_masked_wall(wall)
            if masked is not None:
                return ZahlenmauerPuzzle(
                    base_size=self.base_size,
                    full_wall=wall,
                    masked_wall=masked,
                    difficulty=self.difficulty,
                )

        raise RuntimeError(
            f"Failed to generate a solvable Zahlenmauer within 100 attempts "
            f"(base_size={self.base_size}, difficulty={self.difficulty.value}, max_value={self.max_value})"
        )

    def _generate_full_wall(self) -> list[list[int]]:
        B = self.base_size
        # Maximum allowed per base cell roughly: max_value // (2^(B-1))
        max_base_estimate = max(self.min_value + 1, self.max_value // (2 ** (B - 1)))

        for _ in range(200):
            base = [
                self.rng.randint(self.min_value, max_base_estimate)
                for _ in range(B)
            ]

            # Compute apex directly via binomial coefficients
            apex = sum(math.comb(B - 1, k) * base[k] for k in range(B))
            if self.min_value <= apex <= self.max_value:
                # Build complete wall
                wall = [[0] * (B - r) for r in range(B)]
                wall[0] = base
                for r in range(1, B):
                    for c in range(B - r):
                        wall[r][c] = wall[r - 1][c] + wall[r - 1][c + 1]
                return wall

        # Fallback with minimum values guaranteed to fit
        base = [self.min_value] * B
        wall = [[0] * (B - r) for r in range(B)]
        wall[0] = base
        for r in range(1, B):
            for c in range(B - r):
                wall[r][c] = wall[r - 1][c] + wall[r - 1][c + 1]
        return wall

    def _create_masked_wall(self, full_wall: list[list[int]]) -> Optional[list[list[Optional[int]]]]:
        B = self.base_size
        all_cells = [(r, c) for r in range(B) for c in range(B - r)]
        total_cells = len(all_cells)

        if self.difficulty == Difficulty.EASY:
            target_clues = min(total_cells - 1, B + 2)
            allow_algebraic = False
        elif self.difficulty == Difficulty.MEDIUM:
            target_clues = min(total_cells - 1, B + 1)
            allow_algebraic = False
        else:  # HARD
            target_clues = B
            allow_algebraic = True

        for _ in range(150):
            if self.difficulty == Difficulty.EASY and self.rng.random() < 0.6:
                # Often give the whole base row plus a couple mid clues
                selected = [(0, c) for c in range(B)]
                remaining = [cell for cell in all_cells if cell not in selected]
                self.rng.shuffle(remaining)
                selected.extend(remaining[: target_clues - B])
            else:
                selected = self.rng.sample(all_cells, target_clues)

            known = {cell: full_wall[cell[0]][cell[1]] for cell in selected}
            is_solved, history = ZahlenmauerSolver.solve(
                B, known, allow_algebraic=allow_algebraic
            )

            if is_solved:
                # Validate difficulty characteristics:
                if self.difficulty == Difficulty.EASY:
                    # Easy should not have more than 1 subtraction
                    sub_count = sum(1 for step, _ in history if step == "sub")
                    if sub_count > 1:
                        continue
                elif self.difficulty == Difficulty.HARD:
                    # Hard should ideally require subtraction or algebraic steps
                    add_only = all(step == "add" for step, _ in history)
                    if add_only and B >= 3:
                        continue

                # Build masked 2D grid
                masked: list[list[Optional[int]]] = [
                    [None] * (B - r) for r in range(B)
                ]
                for r, c in selected:
                    masked[r][c] = full_wall[r][c]
                return masked

        return None
