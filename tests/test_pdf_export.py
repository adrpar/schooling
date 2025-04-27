import os
import unittest
from click.testing import CliRunner
from cli.addsub import addsub
from cli.mathrally import mathrally


class TestPDFExport(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.addsub_output_svg = "test_addsub.svg"
        self.addsub_output_pdf = "test_addsub.pdf"
        self.mathrally_output_svg = "test_mathrally.svg"
        self.mathrally_output_pdf = "test_mathrally.pdf"
        self.mathrally_solution_svg = "test_mathrally_solution.svg"
        self.mathrally_solution_pdf = "test_mathrally_solution.pdf"

    def tearDown(self):
        # Clean up generated files
        for file in [
            self.addsub_output_svg,
            self.addsub_output_pdf,
            self.mathrally_output_svg,
            self.mathrally_output_pdf,
            self.mathrally_solution_svg,
            self.mathrally_solution_pdf,
        ]:
            if os.path.exists(file):
                os.remove(file)

    def test_addsub_svg_only(self):
        result = self.runner.invoke(addsub, ["--output", self.addsub_output_svg, "--format", "svg"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(self.addsub_output_svg))
        self.assertFalse(os.path.exists(self.addsub_output_pdf))

    def test_addsub_pdf_only(self):
        result = self.runner.invoke(addsub, ["--output", self.addsub_output_svg, "--format", "pdf"])
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(os.path.exists(self.addsub_output_svg))
        self.assertTrue(os.path.exists(self.addsub_output_pdf))

    def test_addsub_both(self):
        result = self.runner.invoke(addsub, ["--output", self.addsub_output_svg, "--format", "both"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(self.addsub_output_svg))
        self.assertTrue(os.path.exists(self.addsub_output_pdf))

    def test_mathrally_svg_only(self):
        result = self.runner.invoke(mathrally, ["--output", self.mathrally_output_svg, "--solution", self.mathrally_solution_svg, "--format", "svg"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(self.mathrally_output_svg))
        self.assertTrue(os.path.exists(self.mathrally_solution_svg))
        self.assertFalse(os.path.exists(self.mathrally_output_pdf))
        self.assertFalse(os.path.exists(self.mathrally_solution_pdf))

    def test_mathrally_pdf_only(self):
        result = self.runner.invoke(mathrally, ["--output", self.mathrally_output_svg, "--solution", self.mathrally_solution_svg, "--format", "pdf"])
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(os.path.exists(self.mathrally_output_svg))
        self.assertFalse(os.path.exists(self.mathrally_solution_svg))
        self.assertTrue(os.path.exists(self.mathrally_output_pdf))
        self.assertTrue(os.path.exists(self.mathrally_solution_pdf))

    def test_mathrally_both(self):
        result = self.runner.invoke(mathrally, ["--output", self.mathrally_output_svg, "--solution", self.mathrally_solution_svg, "--format", "both"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(self.mathrally_output_svg))
        self.assertTrue(os.path.exists(self.mathrally_solution_svg))
        self.assertTrue(os.path.exists(self.mathrally_output_pdf))
        self.assertTrue(os.path.exists(self.mathrally_solution_pdf))


if __name__ == "__main__":
    unittest.main()
