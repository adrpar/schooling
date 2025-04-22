import unittest
import lxml.etree as ET
from svg.svg_groups import (
    calculate_group_dimensions,
    parse_transform,
    distribute_groups_in_drawing_area,
)


class TestSvgGroups(unittest.TestCase):
    def setUp(self):
        self.svg_content = """
        <svg xmlns="http://www.w3.org/2000/svg">
            <g id="group1" transform="translate(10, 20)">
                <rect x="0" y="0" width="50" height="30"/>
                <rect x="60" y="10" width="40" height="20"/>
                <g id="nested_group" transform="translate(5, 5)">
                    <rect x="0" y="0" width="20" height="10"/>
                </g>
            </g>
        </svg>
        """
        self.svg_tree = ET.fromstring(self.svg_content)
        self.group = self.svg_tree.find(".//{*}g[@id='group1']")

    def test_parse_transform(self):
        transform = "translate(10, 20)"
        x, y = parse_transform(transform)
        self.assertEqual(x, 10)
        self.assertEqual(y, 20)

        transform = "translate(15)"
        x, y = parse_transform(transform)
        self.assertEqual(x, 15)
        self.assertEqual(y, 0)

        transform = None
        x, y = parse_transform(transform)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

    def test_calculate_group_dimensions(self):
        dimensions = calculate_group_dimensions(self.group)
        self.assertEqual(dimensions["width"], 100, "Incorrect width calculated.")
        self.assertEqual(dimensions["height"], 30, "Incorrect height calculated.")

    def test_distribute_groups_in_drawing_area(self):
        drawing_area = ET.Element("rect", x="0", y="0", width="200", height="100")
        drawing_area_group = ET.Element("g")
        group1 = ET.Element("g", id="group1")
        group2 = ET.Element("g", id="group2")
        group3 = ET.Element("g", id="group3")
        group4 = ET.Element("g", id="group4")
        group5 = ET.Element("g", id="group5")

        # Add rectangles to groups to simulate dimensions
        ET.SubElement(group1, "rect", x="0", y="0", width="50", height="30")
        ET.SubElement(group2, "rect", x="0", y="0", width="60", height="40")
        ET.SubElement(group3, "rect", x="0", y="0", width="70", height="20")
        ET.SubElement(group4, "rect", x="0", y="0", width="80", height="30")
        ET.SubElement(group5, "rect", x="0", y="0", width="90", height="40")

        group_list = [group1, group2, group3, group4, group5]

        distribute_groups_in_drawing_area(group_list, drawing_area, drawing_area_group)

        # Verify the groups are distributed correctly
        self.assertEqual(
            len(drawing_area_group),
            5,
            "Not all groups were added to the drawing area group.",
        )

        transforms = [elem.attrib["transform"] for elem in drawing_area_group]
        self.assertEqual(
            transforms[0], "translate(0.0,0.0)", "Group1 transform is incorrect."
        )
        self.assertEqual(
            transforms[1], "translate(60.0,0.0)", "Group2 transform is incorrect."
        )
        self.assertEqual(
            transforms[2], "translate(130.0,0.0)", "Group3 transform is incorrect."
        )
        self.assertEqual(
            transforms[3],
            "translate(0.0,50.0)",
            "Group4 transform is incorrect (should be on the next line).",
        )
        self.assertEqual(
            transforms[4],
            "translate(110.0,50.0)",
            "Group5 transform is incorrect (should be on the next line).",
        )


if __name__ == "__main__":
    unittest.main()
