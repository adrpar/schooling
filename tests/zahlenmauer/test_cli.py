import os
import tempfile
import unittest
from click.testing import CliRunner

from cli.zahlenmauer import zahlenmauer


class TestZahlenmauerCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_svg_only(self):
        output = os.path.join(self.temp_dir.name, "out.svg")
        solution = os.path.join(self.temp_dir.name, "sol.svg")
        result = self.runner.invoke(
            zahlenmauer,
            ["--output", output, "--solution", solution, "--format", "svg", "--seed", "42"],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(output))
        self.assertTrue(os.path.exists(solution))
        self.assertFalse(os.path.exists(output.replace(".svg", ".pdf")))

    def test_cli_both_svg_and_pdf(self):
        output = os.path.join(self.temp_dir.name, "out.svg")
        solution = os.path.join(self.temp_dir.name, "sol.svg")
        result = self.runner.invoke(
            zahlenmauer,
            [
                "--output", output,
                "--solution", solution,
                "--format", "both",
                "--difficulty", "easy",
                "--base-size", "3",
                "--seed", "99",
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(output))
        self.assertTrue(os.path.exists(solution))
        self.assertTrue(os.path.exists(output.replace(".svg", ".pdf")))
        self.assertTrue(os.path.exists(solution.replace(".svg", ".pdf")))


if __name__ == "__main__":
    unittest.main()
