import unittest
from mathrally.algorithm import RallyAlgorithm, Operator


class TestRallyAlgorithm(unittest.TestCase):
    def setUp(self):
        self.operator_list = [
            Operator.ADDITION,
            Operator.SUBTRACTION,
            Operator.MULTIPLICATION,
            Operator.DIVISION,
        ]
        self.min_value = 1
        self.max_value = 100
        self.num_operators = 5
        self.rand_seed = 42

    def test_initialization(self):
        algorithm = RallyAlgorithm(
            self.operator_list,
            self.min_value,
            self.max_value,
            self.num_operators,
            self.rand_seed,
        )
        self.assertEqual(algorithm.operations, self.operator_list)
        self.assertEqual(algorithm.min_value, self.min_value)
        self.assertEqual(algorithm.max_value, self.max_value)
        self.assertEqual(algorithm.num_operators, self.num_operators)
        self.assertEqual(algorithm.seed, self.rand_seed)

    def test_build_rally(self):
        algorithm = RallyAlgorithm(
            self.operator_list,
            self.min_value,
            self.max_value,
            self.num_operators,
            self.rand_seed,
        )
        algorithm.build_rally()
        self.assertEqual(
            len(algorithm.result), self.num_operators + 1
        )  # Includes the starting value
        for i, (operator, value, result) in enumerate(algorithm.result[1:], start=1):
            self.assertIn(operator, self.operator_list)
            self.assertGreaterEqual(result, self.min_value)
            self.assertLessEqual(result, self.max_value)

    def test_choice_criterium(self):
        algorithm = RallyAlgorithm(
            self.operator_list,
            self.min_value,
            self.max_value,
            self.num_operators,
            self.rand_seed,
        )
        results = [(None, None, 50)]
        self.assertTrue(algorithm.choice_criterium(60, Operator.ADDITION, 10, results))
        self.assertFalse(
            algorithm.choice_criterium(0, Operator.SUBTRACTION, 60, results)
        )
        self.assertFalse(
            algorithm.choice_criterium(101, Operator.ADDITION, 51, results)
        )

    def test_no_solution_exception(self):
        algorithm = RallyAlgorithm([Operator.DIVISION], 1, 10, 1, self.rand_seed)
        with self.assertRaises(RuntimeError):
            algorithm.build_rally()


if __name__ == "__main__":
    unittest.main()
