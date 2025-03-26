import unittest
from click.testing import CliRunner
from cli.mathrally import mathrally

class TestMathRally(unittest.TestCase):
    def test_mathrally(self):
        runner = CliRunner()
        result = runner.invoke(mathrally, ['--output', 'test_rally.svg', '--solution', 'test_solution.svg'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Rally generated', result.output)

if __name__ == '__main__':
    unittest.main()
