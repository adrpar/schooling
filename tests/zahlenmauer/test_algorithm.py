import unittest
from exercises.zahlenmauer.algorithm import (
    Difficulty,
    ZahlenmauerAlgorithm,
    ZahlenmauerPuzzle,
    ZahlenmauerSolver,
)


class TestZahlenmauerAlgorithm(unittest.TestCase):
    def test_difficulty_enum(self):
        self.assertEqual(Difficulty.from_string("easy"), Difficulty.EASY)
        self.assertEqual(Difficulty.from_string("MEDIUM"), Difficulty.MEDIUM)
        self.assertEqual(Difficulty.from_string("hard"), Difficulty.HARD)
        with self.assertRaises(ValueError):
            Difficulty.from_string("expert")

    def test_base_size_validation(self):
        with self.assertRaises(ValueError):
            ZahlenmauerAlgorithm(base_size=2)
        with self.assertRaises(ValueError):
            ZahlenmauerAlgorithm(base_size=11)

    def test_max_value_validation(self):
        # Base size 4 has minimum apex of 2^3 * 1 = 8
        with self.assertRaises(ValueError):
            ZahlenmauerAlgorithm(base_size=4, min_value=1, max_value=7)

    def test_full_wall_arithmetic(self):
        alg = ZahlenmauerAlgorithm(base_size=4, max_value=100, num_pyramids=3, rand_seed=42)
        puzzles = alg.build()
        self.assertEqual(len(puzzles), 3)

        for p in puzzles:
            wall = p.full_wall
            self.assertEqual(len(wall), 4)
            # Verify addition law: wall[r][c] == wall[r-1][c] + wall[r-1][c+1]
            for r in range(1, 4):
                for c in range(4 - r):
                    self.assertEqual(
                        wall[r][c],
                        wall[r - 1][c] + wall[r - 1][c + 1],
                        f"Failed addition at row {r}, col {c}",
                    )
            # Apex must be <= max_value
            self.assertLessEqual(wall[-1][0], 100)
            # All base values >= min_value
            for val in wall[0]:
                self.assertGreaterEqual(val, 1)

    def test_easy_difficulty_clues_and_solvability(self):
        alg = ZahlenmauerAlgorithm(
            base_size=4, difficulty=Difficulty.EASY, max_value=100, num_pyramids=5, rand_seed=10
        )
        puzzles = alg.build()

        for p in puzzles:
            clues = {
                (r, c): p.masked_wall[r][c]
                for r in range(4)
                for c in range(4 - r)
                if p.masked_wall[r][c] is not None
            }
            # Easy gives B + 2 clues (6 clues for base 4)
            self.assertEqual(len(clues), 6)
            is_solved, history = ZahlenmauerSolver.solve(4, clues, allow_algebraic=False)
            self.assertTrue(is_solved, "Easy puzzle should be completely solvable")
            # Easy has at most 1 subtraction
            sub_count = sum(1 for step, _ in history if step == "sub")
            self.assertLessEqual(sub_count, 1)

    def test_medium_difficulty_solvability(self):
        alg = ZahlenmauerAlgorithm(
            base_size=4, difficulty=Difficulty.MEDIUM, max_value=100, num_pyramids=5, rand_seed=20
        )
        puzzles = alg.build()

        for p in puzzles:
            clues = {
                (r, c): p.masked_wall[r][c]
                for r in range(4)
                for c in range(4 - r)
                if p.masked_wall[r][c] is not None
            }
            # Medium gives B + 1 clues (5 clues for base 4)
            self.assertEqual(len(clues), 5)
            # Solvable step-by-step with NO algebraic guessing
            is_solved, history = ZahlenmauerSolver.solve(4, clues, allow_algebraic=False)
            self.assertTrue(is_solved, "Medium puzzle must be solvable without algebra")
            # All steps must be add or sub
            self.assertTrue(all(step in ("add", "sub") for step, _ in history))

    def test_hard_difficulty_minimal_clues(self):
        alg = ZahlenmauerAlgorithm(
            base_size=4, difficulty=Difficulty.HARD, max_value=100, num_pyramids=5, rand_seed=30
        )
        puzzles = alg.build()

        for p in puzzles:
            clues = {
                (r, c): p.masked_wall[r][c]
                for r in range(4)
                for c in range(4 - r)
                if p.masked_wall[r][c] is not None
            }
            # Hard gives exactly base_size clues (minimal 4 clues)
            self.assertEqual(len(clues), 4)
            is_solved, _ = ZahlenmauerSolver.solve(4, clues, allow_algebraic=True)
            self.assertTrue(is_solved, "Hard puzzle must be solvable")

    def test_rng_isolation(self):
        alg1 = ZahlenmauerAlgorithm(base_size=4, rand_seed=999)
        alg2 = ZahlenmauerAlgorithm(base_size=4, rand_seed=999)
        alg3 = ZahlenmauerAlgorithm(base_size=4, rand_seed=123)

        p1 = alg1.build()
        p2 = alg2.build()
        p3 = alg3.build()

        self.assertEqual(p1[0].full_wall, p2[0].full_wall)
        self.assertEqual(p1[0].masked_wall, p2[0].masked_wall)
        self.assertNotEqual(p1[0].full_wall, p3[0].full_wall)

    def test_optimal_pyramid_count(self):
        from exercises.zahlenmauer.algorithm import get_optimal_pyramid_count
        self.assertEqual(get_optimal_pyramid_count(3), 6)
        self.assertEqual(get_optimal_pyramid_count(6), 6)
        self.assertEqual(get_optimal_pyramid_count(7), 2)
        self.assertEqual(get_optimal_pyramid_count(8), 2)
        self.assertEqual(get_optimal_pyramid_count(9), 1)
        self.assertEqual(get_optimal_pyramid_count(10), 1)

        # Default initialization uses optimal count
        alg_4 = ZahlenmauerAlgorithm(base_size=4)
        self.assertEqual(alg_4.num_pyramids, 6)
        alg_7 = ZahlenmauerAlgorithm(base_size=7)
        self.assertEqual(alg_7.num_pyramids, 2)


if __name__ == "__main__":
    unittest.main()
