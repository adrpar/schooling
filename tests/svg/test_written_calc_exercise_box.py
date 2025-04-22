import unittest
from addSubWritten.addsub import Operator
import lxml.etree as ET
from svg.number_paper.written_calc_exercise_box import WrittenCalcExerciseBox

class TestWrittenCalcExerciseBox(unittest.TestCase):
    def setUp(self):
        self.operation = Operator.ADDITION
        self.values = [123, 456]
        self.exercise_box = WrittenCalcExerciseBox(self.operation, self.values)

    def test_generate_box_structure(self):
        box = self.exercise_box.generateBox()
        self.assertEqual(box.tag, "g")
        self.assertEqual(box.attrib["id"], "exerciseBox")
        self.assertIn("transform", box.attrib)

    def test_generate_box_content(self):
        box = self.exercise_box.generateBox()
        rects = box.findall(".//{*}rect")
        
        x_dimensions, y_dimensions = self._count_distinct_translate_values(box)
        self.assertEqual(len(x_dimensions), 7, "Incorrect number of x boxes found.")
        self.assertEqual(len(y_dimensions), 4, "Incorrect number of y boxes found.")

        texts = box.findall(".//{*}text")
        self.assertGreater(len(rects), 0, "No rectangles found in the generated box.")
        self.assertGreater(len(texts), 0, "No text elements found in the generated box.")

        lines = box.findall(".//{*}line")
        self.assertGreater(len(lines), 0, "No lines found in the generated box.")

    def test_operator_in_box(self):
        box = self.exercise_box.generateBox()

        texts = box.findall(".//{*}tspan")
        operator_found = any(text.text == "+" for text in texts if text.text)
        self.assertTrue(operator_found, "Operator not found in the generated box.")

    def test_values_in_box(self):
        box = self.exercise_box.generateBox()
        texts = box.findall(".//{*}tspan")
        for value in self.values:
            value_found = any(text.text in list("123456") for text in texts if text.text)
            self.assertTrue(value_found, f"Value {value} not found in the generated box.")

    def _count_distinct_translate_values(self, box):
        # Find all elements with a transform attribute
        transform_elements = box.xpath(".//*[@transform]")
        
        x_values = set()
        y_values = set()
        
        for element in transform_elements:
            transform = element.attrib.get("transform", "")
            if "translate" in transform:
                # Extract the translate values using regex
                import re
                match = re.search(r"translate\(([^,]+),\s*([^)]+)\)", transform)
                if match:
                    x, y = match.groups()
                    x_values.add(float(x))
                    y_values.add(float(y))

        return x_values, y_values    

if __name__ == '__main__':
    unittest.main()
