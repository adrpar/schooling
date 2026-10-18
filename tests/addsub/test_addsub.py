import unittest
from click.testing import CliRunner
from cli.addsub import addsub


class TestAddSub(unittest.TestCase):
    def test_addsub(self):
        runner = CliRunner()
        result = runner.invoke(addsub, ["--output", "test_addsub.svg"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Add/Sub exercises generated", result.output)


if __name__ == "__main__":
    unittest.main()
