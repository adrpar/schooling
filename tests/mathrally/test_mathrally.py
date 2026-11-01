import unittest
from click.testing import CliRunner
from cli.mathrally import mathrally

class TestMathRally(unittest.TestCase):
    def tearDown(self):
        import os
        for f in [
            "test_rally.svg",
            "test_solution.svg",
            "test_rally2_cli.svg",
            "test_rally2_solution_cli.svg",
            "test_rally2_cli.pdf",
            "test_rally2_solution_cli.pdf",
            "test.svg",
            "test_res.svg",
        ]:
            if os.path.exists(f):
                os.remove(f)

    def test_mathrally(self):
        runner = CliRunner()
        result = runner.invoke(
            mathrally, ["--output", "test_rally.svg", "--solution", "test_solution.svg"]
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Rally generated", result.output)

    def test_mathrally_rally2_template(self):
        runner = CliRunner()
        result = runner.invoke(
            mathrally,
            [
                "--template",
                "Rally2.svg",
                "--output",
                "test_rally2_cli.svg",
                "--solution",
                "test_rally2_solution_cli.svg",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Rally generated", result.output)


if __name__ == "__main__":
    unittest.main()

