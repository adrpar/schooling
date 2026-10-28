import os
import tempfile
import unittest
import lxml.etree as ET

from exercises.zahlenmauer.algorithm import ZahlenmauerAlgorithm, Difficulty
from exercises.zahlenmauer.template import ZahlenmauerTemplate
from svg.svg_handler import NAMESPACE_MAP, SVGFile


class TestZahlenmauerTemplate(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.student_path = os.path.join(self.temp_dir.name, "test_student.svg")
        self.solution_path = os.path.join(self.temp_dir.name, "test_solution.svg")
        self.alg = ZahlenmauerAlgorithm(
            base_size=4,
            difficulty=Difficulty.MEDIUM,
            num_pyramids=4,
            rand_seed=42,
        )
        self.template = ZahlenmauerTemplate()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_sheets_generates_valid_svg_files(self):
        self.template.create_sheets(self.alg, self.student_path, self.solution_path)
        self.assertTrue(os.path.exists(self.student_path))
        self.assertTrue(os.path.exists(self.solution_path))

        # Check that both are valid XML/SVG
        student_file = SVGFile(self.student_path)
        solution_file = SVGFile(self.solution_path)

        # Drawing area must contain 4 pyramids
        student_pyramids = [
            g for g in student_file.find_all("g")
            if g.attrib.get("id", "").startswith("pyramid_")
        ]
        self.assertEqual(len(student_pyramids), 4)

        solution_pyramids = [
            g for g in solution_file.find_all("g")
            if g.attrib.get("id", "").startswith("pyramid_")
        ]
        self.assertEqual(len(solution_pyramids), 4)

    def test_brick_count_and_blanks(self):
        self.template.create_sheets(self.alg, self.student_path, self.solution_path)
        student_file = SVGFile(self.student_path)
        solution_file = SVGFile(self.solution_path)

        first_student_pyramid = student_file.find_all("g[@id='pyramid_1']")[0]
        first_solution_pyramid = solution_file.find_all("g[@id='pyramid_1']")[0]

        # For base_size=4, there are 4+3+2+1 = 10 bricks per pyramid
        student_rects = first_student_pyramid.findall(".//rect", namespaces=NAMESPACE_MAP)
        self.assertEqual(len(student_rects), 10)

        solution_rects = first_solution_pyramid.findall(".//rect", namespaces=NAMESPACE_MAP)
        self.assertEqual(len(solution_rects), 10)

        # In student sheet, blank bricks don't have text; given clues do (+ 1 label "#1")
        student_texts = first_student_pyramid.findall(".//text", namespaces=NAMESPACE_MAP)
        # 5 clues + 1 label = 6 texts
        self.assertEqual(len(student_texts), 6)

        # In solution sheet, all 10 bricks have text (+ 1 label "#1" = 11 texts)
        solution_texts = first_solution_pyramid.findall(".//text", namespaces=NAMESPACE_MAP)
        self.assertEqual(len(solution_texts), 11)


if __name__ == "__main__":
    unittest.main()
