import os
import unittest
from pathlib import Path

from svg.canvas_template import CanvasExerciseTemplate
from svg.svg_handler import SvgElement


class TestCanvasExerciseTemplate(unittest.TestCase):
    def setUp(self):
        self.canvas_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297">
          <g id="drawingArea">
            <rect id="drawingAreaRect" x="10" y="20" width="180" height="240"/>
          </g>
          <text id="Title">
            <tspan id="TitleSpan">Initial Title</tspan>
            <tspan id="ConfigSpan">Initial Config</tspan>
          </text>
        </svg>"""
        self.template_path = "test_canvas.svg"
        with open(self.template_path, "w") as f:
            f.write(self.canvas_svg)
        self.template = CanvasExerciseTemplate(self.template_path)

    def tearDown(self):
        if os.path.exists(self.template_path):
            os.remove(self.template_path)

    def test_init_finds_drawing_area_and_title(self):
        self.assertIsNotNone(self.template.drawing_area)
        self.assertEqual(self.template.drawing_area.attrib["id"], "drawingAreaRect")
        self.assertIn("TitleSpan", self.template.title_tspans)
        self.assertIn("ConfigSpan", self.template.title_tspans)

    def test_set_title_and_config(self):
        self.template.set_title("New Title")
        self.template.set_config_text("Config 123")
        self.assertEqual(self.template.title_tspans["TitleSpan"].text, "New Title")
        self.assertEqual(self.template.title_tspans["ConfigSpan"].text, "Config 123")

    def test_clone_independence(self):
        cloned = self.template.clone()
        cloned.set_title("Cloned Title")
        self.assertEqual(self.template.title_tspans["TitleSpan"].text, "Initial Title")
        self.assertEqual(cloned.title_tspans["TitleSpan"].text, "Cloned Title")

    def test_distribute_exercises(self):
        boxes = []
        for i in range(3):
            g = SvgElement("g", attrib={"id": f"box_{i}"})
            g.create_child("rect", attrib={"x": "0", "y": "0", "width": "20", "height": "20"})
            boxes.append(g)

        self.template.distribute_exercises(boxes)
        children = self.template.drawing_area_group.find_all("g")
        self.assertEqual(len(children), 3)

    def test_set_header(self):
        self.template.set_header("Awesome Title", "Awesome Subtitle")
        self.assertEqual(self.template.title_tspans["TitleSpan"].text, "Awesome Title")
        self.assertEqual(self.template.title_tspans["ConfigSpan"].text, "Awesome Subtitle")
        self.assertIn("font-size:7.5px", self.template.title_tspans["TitleSpan"].attrib["style"])
        self.assertIn("font-size:3.6px", self.template.title_tspans["ConfigSpan"].attrib["style"])

    def test_set_footer_visibility_and_text(self):
        self.template.set_footer("Name: Alice    Datum: 2026-10-10", visible=True)
        self.assertIsNotNone(self.template.footer_element)
        self.assertEqual(self.template.footer_span.text, "Name: Alice    Datum: 2026-10-10")
        self.assertIn("font-size:3.5px", self.template.footer_span.attrib["style"])

        # Hide footer
        self.template.set_footer(visible=False)
        self.assertIsNone(self.template.footer_element)

    def test_create_exercise_label(self):
        label = CanvasExerciseTemplate.create_exercise_label(5)
        self.assertEqual(label.tag, "text")
        self.assertEqual(label.text, "#5")
        self.assertIn("font-size:3.2px", label.attrib["style"])

    def test_auto_create_config_span_if_missing(self):
        minimal_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 297">
          <g id="drawingArea"><rect id="drawingAreaRect" x="0" y="0" width="100" height="100"/></g>
          <text id="Title"><tspan id="TitleSpan">Only Title</tspan></text>
        </svg>"""
        path = "test_minimal.svg"
        with open(path, "w") as f:
            f.write(minimal_svg)
        tmpl = CanvasExerciseTemplate(path)
        self.assertNotIn("ConfigSpan", tmpl.title_tspans)
        tmpl.set_config_text("Created Subtitle")
        self.assertIn("ConfigSpan", tmpl.title_tspans)
        self.assertEqual(tmpl.title_tspans["ConfigSpan"].text, "Created Subtitle")
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    unittest.main()

