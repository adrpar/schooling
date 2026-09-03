import copy

import lxml.etree as ET

# Cell geometry constants (sourced from original Inkscape template)
_CELL_SIZE = 5.8861966        # width and height of the grid square
_CELL_STROKE_WIDTH = 0.223193
_TEXT_FONT_SIZE = 4.93889     # px, matches original template
_TEXT_X = _CELL_SIZE / 2     # centred horizontally (text-anchor: middle)
_TEXT_Y = 4.7672572           # baseline position that centres text vertically in the cell

# Pre-built prototype elements — constructed once at module load, deep-copied per cell (Q25)
_PROTO_GROUP: ET.Element
_PROTO_TEXT: ET.Element
_PROTO_TSPAN: ET.Element
_PROTO_RECT: ET.Element


def _build_prototypes():
    global _PROTO_GROUP, _PROTO_TEXT, _PROTO_TSPAN, _PROTO_RECT

    _PROTO_GROUP = ET.Element("g", transform="translate(0.0,0.0)")

    _PROTO_TEXT = ET.SubElement(
        _PROTO_GROUP,
        "text",
        attrib={
            "x": str(_TEXT_X),
            "y": str(_TEXT_Y),
            "id": "text_template",
            "style": (
                f"font-style:normal;font-variant:normal;font-weight:normal;"
                f"font-stretch:normal;font-size:{_TEXT_FONT_SIZE}px;"
                f"font-family:Helvetica;text-align:center;"
                f"text-anchor:middle;dominant-baseline:auto;"
                f"fill:#000000;stroke-width:0.264583"
            ),
        },
    )

    _PROTO_TSPAN = ET.SubElement(
        _PROTO_TEXT,
        "tspan",
        attrib={
            "x": str(_TEXT_X),
            "y": str(_TEXT_Y),
            "id": "tspan_template",
            "style": (
                f"font-style:normal;font-variant:normal;font-weight:normal;"
                f"font-stretch:normal;font-size:{_TEXT_FONT_SIZE}px;"
                f"font-family:Helvetica;stroke-width:0.264583"
            ),
        },
    )
    _PROTO_TSPAN.text = ""

    _PROTO_RECT = ET.SubElement(
        _PROTO_GROUP,
        "rect",
        attrib={
            "id": "rect_template",
            "x": "0",
            "y": "0",
            "width": str(_CELL_SIZE),
            "height": str(_CELL_SIZE),
            "style": (
                f"fill:none;stroke:#000000;"
                f"stroke-width:{_CELL_STROKE_WIDTH};"
                f"stroke-dasharray:none;stroke-opacity:1"
            ),
        },
    )


_build_prototypes()


class NumericalPaperCell:
    # Keep class-level maps for external callers that reference these
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
        # Deep-copy the prototype tree instead of re-parsing XML (Q25)
        self.group = copy.deepcopy(_PROTO_GROUP)

        texts = self.group.findall(".//text")
        self.text = texts[0] if texts else None

        tspans = self.group.findall(".//tspan")
        self.tspan = tspans[0] if tspans else None

        rects = self.group.findall(".//rect")
        self.rect = rects[0] if rects else None

        self.tspan.text = str(value) if value else ""
        if value in self.OPERATOR_DETECTION:
            self._handle_operators(value)

    def _handle_operators(self, value):
        """Normalise operator glyphs. With text-anchor:middle, no x-nudging needed. (Q28)"""
        if self.text is None or self.tspan is None:
            return
        if value in self.MULTIPLICATION_DETECTION:
            self.tspan.text = self.OPERATORS[2]  # ×
        elif value in self.DIVISION_DETECTION:
            self.tspan.text = self.OPERATORS[3]  # ÷
        # +, -, and the unicode variants are already correct as-is

    def _remove_text(self):
        self.group.remove(self.text)
        self.text = None
        self.tspan = None
