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


class ZahlenmauerSolver:
    @staticmethod
    def solve(
        base_size: int,
        known_cells: dict[tuple[int, int], int],
        allow_algebraic: bool = False,
    ) -> tuple[bool, list[tuple[str, tuple[int, int]]]]:
        """
        Simulates step-by-step student deduction on a Zahlenmauer.

        :param base_size: Number of bricks at the bottom row.
        :param known_cells: Map of (row, col) -> value of given clues.
        :param allow_algebraic: Whether to allow linear combination puzzle steps (e.g. 2b = Top - a - c).
        :return: (is_completely_solved, deduction_history)
        """
        current = dict(known_cells)
        history: list[tuple[str, tuple[int, int]]] = []

        while True:
            progress = False

            # 1. Step-by-step triangular additions and subtractions
            for r in range(1, base_size):
                for c in range(base_size - r):
                    p = (r, c)
                    l = (r - 1, c)
                    right = (r - 1, c + 1)

                    # Upward addition: Left + Right = Parent
                    if l in current and right in current and p not in current:
                        current[p] = current[l] + current[right]
                        history.append(("add", p))
                        progress = True
                    # Downward subtraction: Parent - Left = Right
                    elif p in current and l in current and right not in current:
                        val = current[p] - current[l]
                        if val < 0:
                            return False, history
                        current[right] = val
                        history.append(("sub", right))
                        progress = True
                    # Downward subtraction: Parent - Right = Left
                    elif p in current and right in current and l not in current:
                        val = current[p] - current[right]
                        if val < 0:
                            return False, history
                        current[l] = val
                        history.append(("sub", l))
                        progress = True

            if progress:
                continue

            # 2. Algebraic single-variable reduction (Knobelaufgabe, for Hard)
            if allow_algebraic:
                for r in range(1, base_size):
                    for c in range(base_size - r):
                        if (r, c) in current:
                            target_val = current[(r, c)]
                            unknowns: list[tuple[tuple[int, int], int]] = []
                            known_sum = 0

                            for k in range(r + 1):
                                base_cell = (0, c + k)
                                coeff = math.comb(r, k)
                                if base_cell in current:
                                    known_sum += coeff * current[base_cell]
                                else:
                                    unknowns.append((base_cell, coeff))

                            if len(unknowns) == 1:
                                target_cell, coeff = unknowns[0]
                                rem = target_val - known_sum
                                if rem > 0 and rem % coeff == 0:
                                    current[target_cell] = rem // coeff
                                    history.append(("algebraic", target_cell))
                                    progress = True
                                    break
                    if progress:
                        break

            if not progress:
                break

        total_cells = base_size * (base_size + 1) // 2
        is_solved = len(current) == total_cells
        return is_solved, history


class ZahlenmauerAlgorithm:
    def __init__(
        self,
        base_size: int = 4,
        difficulty: Difficulty = Difficulty.MEDIUM,
        min_value: int = 1,
        max_value: int = 100,
        num_pyramids: int = 6,
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
        self.num_pyramids = num_pyramids
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
