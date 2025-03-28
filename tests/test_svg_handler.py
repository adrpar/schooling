import unittest
import lxml.etree as ET
from svg.svg_handler import SVGFile, SvgNode

class TestSVGFile(unittest.TestCase):
    def setUp(self):
        # Create a simple SVG content for testing
        self.svg_content = '''<svg xmlns="http://www.w3.org/2000/svg">
            <text id="test_text">Hello</text>
            <rect id="test_rect" width="100" height="100"/>
            <g id="test_group">
                <tspan id="test_tspan">World</tspan>
            </g>
        </svg>'''
        self.file_name = "test.svg"
        with open(self.file_name, "w") as f:
            f.write(self.svg_content)
        self.svg_file = SVGFile(self.file_name)

    def tearDown(self):
        import os
        os.remove(self.file_name)

    def test_find_all(self):
        elements = self.svg_file.find_all("text")
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].attrib["id"], "test_text")

    def test_find_all_elements_by_attributes(self):
        elements = self.svg_file.find_all_elements_by_attributes("rect", "id")
        self.assertIn("test_rect", elements)
        self.assertEqual(elements["test_rect"].attrib["width"], "100")

    def test_find_all_in_node(self):
        group_node = self.svg_file.find_all("g")[0]
        elements = self.svg_file.find_all_in_node(group_node, "tspan")
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].attrib["id"], "test_tspan")

    def test_find_all_elements_by_attributes_in_node(self):
        group_node = self.svg_file.find_all("g")[0]
        elements = self.svg_file.find_all_elements_by_attributes_in_node(group_node, "tspan", "id")
        self.assertIn("test_tspan", elements)
        self.assertEqual(elements["test_tspan"].text, "World")

    def test_all_spans_in_text(self):
        text_node = self.svg_file.find_all("g")[0]
        spans = self.svg_file.all_spans_in_text(text_node)
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0].attrib["id"], "test_tspan")

    def test_write(self):
        new_file_name = "test_output.svg"
        self.svg_file.write(new_file_name)
        with open(new_file_name, "r") as f:
            content = f.read()
        self.assertIn('<svg xmlns="http://www.w3.org/2000/svg">', content)
        import os
        os.remove(new_file_name)

class TestSvgNode(unittest.TestCase):
    def setUp(self):
        # Create a simple SVG content for testing
        self.svg_content = '''<svg xmlns="http://www.w3.org/2000/svg">
            <g id="test_group">
                <tspan id="test_tspan">World</tspan>
            </g>
        </svg>'''
        self.node = ET.fromstring(self.svg_content)
        self.svg_node = SvgNode(self.node)

    def test_find_all_in_node(self):
        elements = self.svg_node.find_all_in_node("tspan")
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0].attrib["id"], "test_tspan")

    def test_find_all_elements_by_attributes_in_node(self):
        elements = self.svg_node.find_all_elements_by_attributes_in_node("tspan", "id")
        self.assertIn("test_tspan", elements)
        self.assertEqual(elements["test_tspan"].text, "World")

if __name__ == '__main__':
    unittest.main()
