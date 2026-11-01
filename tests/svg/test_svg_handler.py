import unittest
import lxml.etree as ET
from svg.svg_handler import SVGFile, SvgNode, SvgElement, SvgDocument


class TestSVGFile(unittest.TestCase):
    def setUp(self):
        # Create a simple SVG content for testing
        self.svg_content = """<svg xmlns="http://www.w3.org/2000/svg">
            <text id="test_text">Hello</text>
            <rect id="test_rect" width="100" height="100"/>
            <g id="test_group">
                <tspan id="test_tspan">World</tspan>
            </g>
        </svg>"""
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
        elements = self.svg_file.find_all_elements_by_attributes_in_node(
            group_node, "tspan", "id"
        )
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
        self.svg_content = """<svg xmlns="http://www.w3.org/2000/svg">
            <g id="test_group">
                <tspan id="test_tspan">World</tspan>
            </g>
        </svg>"""
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


class TestSvgElementAndDocument(unittest.TestCase):
    def test_element_builder_and_properties(self):
        elem = SvgElement("g", attrib={"id": "main_group", "transform": "translate(10,20)"})
        self.assertEqual(elem.tag, "g")
        self.assertEqual(elem.id, "main_group")
        self.assertEqual(elem.attrib["transform"], "translate(10,20)")

        child = elem.create_child("rect", attrib={"x": "5", "y": "5", "width": "50", "height": "20"})
        self.assertEqual(len(elem), 1)
        self.assertEqual(child.tag, "rect")
        self.assertEqual(child.get("width"), "50")

        text = elem.create_child("text", text="Sample")
        self.assertEqual(text.text, "Sample")
        text.text = "Updated"
        self.assertEqual(text.text, "Updated")

    def test_clone_element(self):
        parent = SvgElement("g", attrib={"id": "original"})
        parent.create_child("circle", attrib={"r": "10"})
        cloned = parent.clone()
        cloned.id = "cloned"
        self.assertEqual(parent.id, "original")
        self.assertEqual(cloned.id, "cloned")
        self.assertEqual(len(cloned), 1)

    def test_document_from_string_and_search(self):
        svg_str = '<svg xmlns="http://www.w3.org/2000/svg"><g id="grp"><rect id="r1" width="10"/></g></svg>'
        doc = SvgDocument.from_string(svg_str)
        rect = doc.find_by_id("r1")
        self.assertIsNotNone(rect)
        self.assertEqual(rect.attrib["width"], "10")

        rects = doc.find_all("rect")
        self.assertEqual(len(rects), 1)


if __name__ == "__main__":
    unittest.main()

