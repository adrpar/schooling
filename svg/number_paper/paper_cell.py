import lxml.etree as ET
from svg.svg_handler import SvgNode

BOX_TEMPLATE = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<g id="box_template" transform="translate(0.0,0.0)">
    <text xml:space="preserve" style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.93889px;font-family:Helvetica;-inkscape-font-specification:Helvetica;text-align:start;writing-mode:lr-tb;direction:ltr;text-anchor:start;fill:#000000;stroke-width:0.264583" x="1.5323327" y="4.7672572" id="text_template"><tspan sodipodi:role="line" id="tspan_template" style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.93889px;font-family:Helvetica;-inkscape-font-specification:Helvetica;stroke-width:0.264583" x="1.5323327" y="4.7672572">4</tspan></text>
    <rect style="fill:none;stroke:#000000;stroke-width:0.223193;stroke-dasharray:none;stroke-opacity:1" id="rect_template" width="5.8861966" height="5.8861966" x="0" y="0"/>
</g>
</svg>
"""


class NumericalPaperCell:
    NAMESPACE_MAP = {
        "html": "http://www.w3.org/1999/xhtml",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xmlns": "http://www.w3.org/2000/xmlns/",
        None: "http://www.w3.org/2000/svg",
    }

    OPERATOR_DETECTION = ["+", "-", "x", "*", "/", "×", "÷"]
    MULTIPLICATION_DETECTION = ["x", "*", "×"]
    DIVISION_DETECTION = ["/", "÷"]
    OPERATORS = ["+", "-", "×", "÷"]

    def __init__(self, value=None):
        parser = ET.XMLParser(recover=True)
        self.box_node = SvgNode(ET.fromstring(BOX_TEMPLATE, parser))

        groups = self.box_node.find_all_in_node("g")
        self.group = groups[0]

        texts = self.box_node.find_all_in_node("text")
        self.text = texts[0]

        tspans = self.box_node.find_all_in_node("tspan")
        self.tspan = tspans[0]

        rects = self.box_node.find_all_in_node("rect")
        self.rect = rects[0]

        self.tspan.text = str(value) if value else ""
        if value in self.OPERATOR_DETECTION:
            self._handle_operators(value)

    def _handle_operators(self, value):
        if self.text is None or self.tspan is None:
            return

        self.text.attrib["y"] = "4.2380905"
        self.tspan.attrib["y"] = "4.2380905"
        self.text.attrib["x"] = "1.5323327"
        self.tspan.attrib["x"] = "1.5323327"

        if value == "-":
            self.text.attrib["x"] = "2.0614994"
            self.tspan.attrib["x"] = "2.0614994"
        elif value in self.MULTIPLICATION_DETECTION:
            self.tspan.text = self.OPERATORS[2]
        elif value in self.DIVISION_DETECTION:
            self.tspan.text = self.OPERATORS[3]

    def _remove_text(self):
        self.group.remove(self.text)
        self.text = None
        self.tspan = None
