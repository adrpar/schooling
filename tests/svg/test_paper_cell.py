import unittest
import lxml.etree as ET
from svg.number_paper.paper_cell import NumericalPaperCell


class TestNumericalPaperCell(unittest.TestCase):
    def setUp(self):
        self.value = 4
        self.operator_add = "+"
        self.operator_sub = "-"
        self.cell = NumericalPaperCell(self.value)
        self.operator_add_cell = NumericalPaperCell(self.operator_add)
        self.operator_sub_cell = NumericalPaperCell(self.operator_sub)

    def test_initialization(self):
        self.assertEqual(self.cell.tspan.text, str(self.value))
        self.assertEqual(self.operator_add_cell.tspan.text, self.operator_add)
        self.assertEqual(self.operator_sub_cell.tspan.text, self.operator_sub)

    def test_handle_operators(self):
        multiplication_cell = NumericalPaperCell("x")
        division_cell = NumericalPaperCell("/")
        self.assertEqual(multiplication_cell.tspan.text, "×")
        self.assertEqual(division_cell.tspan.text, "÷")

    def test_remove_text(self):
        self.cell._remove_text()
        self.assertIsNone(self.cell.text)
        self.assertIsNone(self.cell.tspan)


if __name__ == "__main__":
    unittest.main()
