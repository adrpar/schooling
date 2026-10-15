import lxml.etree as ET

from core.operators import Operator
from exercises.utils import operator_to_string
from svg.styles import (
    COLOR_SOLUTION,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    DEFAULT_FOOTER_TEXT,
    FILL_SOLUTION,
    FONT_FAMILY,
    FOOTER_DEFAULT_X,
    FOOTER_DEFAULT_Y,
    get_footer_style,
    get_subtitle_style,
    get_title_style,
)
from svg.svg_handler import NAMESPACE_MAP, SVGFile



class RallyTemplate:
    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"
    TITLE_ID = "Title"

    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"

    def __init__(self, file_name):
        self.file_name = file_name
        self.svg = SVGFile(file_name)

        text_elements = self.svg.find_all_elements_by_attributes("text", "id")

        self.value_elements = {
            key: element
            for key, element in text_elements.items()
            if self.VALUE_ID_PREFIX in key
        }
        self.operator_elements = {
            key: element
            for key, element in text_elements.items()
            if self.OPERATOR_TEXT_ID_PREFIX in key
        }
        self.title_element = text_elements[self.TITLE_ID]

        title_tspan_elements = self.svg.all_spans_in_text(self.title_element)
        self.title_tspan_elements = {
            element.attrib["id"]: element for element in title_tspan_elements
        }
        self._validate_assumptions()

        self.num_operators = len(self.operator_elements.keys())
        self.num_value_elements = len(self.value_elements.keys())

    def _validate_assumptions(self):
        operator_ids = [int(key.split(".")[1]) for key in self.operator_elements.keys()]
        operator_ids = sorted(operator_ids)
        if not all([i == id for i, id in enumerate(operator_ids)]):
            print(operator_ids)
            raise ValueError("Operator ids are not consecutive")

        value_ids = [int(key.split(".")[1]) for key in self.value_elements.keys()]
        value_ids = sorted(value_ids)
        if not all([i == id for i, id in enumerate(value_ids)]):
            print(value_ids)
            raise ValueError("Value ids are not consecutive")

        num_operators = len(self.operator_elements.keys())
        num_value_elements = len(self.value_elements.keys())

        if (num_value_elements - num_operators) != 1:
            print(num_value_elements, num_operators)
            raise ValueError(
                "Template has not one more value field than operations fields"
            )

        if not all(
            [
                element in ["TitleSpan", "ConfigSpan"]
                for element in self.title_tspan_elements.keys()
            ]
        ):
            print(self.title_tspan_elements)
            raise ValueError("Title does not contain expected tspans")

    @staticmethod
    def _calc_value_font_size(text: str) -> float:
        """Scale font to maintain consistent visual width across digit counts.

        Target: text occupies ~60% of the box width (20.75mm -> ~12.5mm).
        Character width is approximately 0.55 * font-size for bold sans-serif.
        """
        l = len(str(text))
        if l <= 1:
            return 6.0
        elif l == 2:
            return 5.5
        elif l == 3:
            return 4.5
        else:
            return 3.8

    @staticmethod
    def _calc_operator_font_size(text: str) -> float:
        l = len(str(text))
        if l <= 2:
            return 4.5
        elif l == 3:
            return 4.1
        else:
            return 3.5

    def _format_value_element(
        self, text_elem, val_text: str, is_solution: bool = False, is_start: bool = False
    ):
        """Cleanly center and style value boxes with adaptive font sizing."""
        if len(text_elem) > 0:
            text_elem[0].text = str(val_text) if val_text else ""
        else:
            text_elem.text = str(val_text) if val_text else ""

        raw_text = text_elem.raw_element if hasattr(text_elem, "raw_element") else text_elem
        raw_parent = raw_text.getparent()
        rect = (
            raw_parent.find("{http://www.w3.org/2000/svg}rect")
            if raw_parent is not None
            else None
        )

        if rect is not None:
            rx = float(rect.attrib.get("x", 33.757515))
            ry = float(rect.attrib.get("y", 57.658085))
            rw = float(rect.attrib.get("width", 20.754112))
            rh = float(rect.attrib.get("height", 12.74199))
            cx = rx + rw / 2.0
            cy = ry + rh / 2.0
        else:
            cx, cy = 44.134571, 64.02908

        # Remove distorting attributes that caused autosize stretching
        for attr in ["transform", "lengthAdjust", "textLength"]:
            text_elem.attrib.pop(attr, None)
        for child in text_elem:
            for attr in ["transform", "lengthAdjust", "textLength"]:
                child.attrib.pop(attr, None)

        fsize = self._calc_value_font_size(val_text)
        is_solved_val = is_solution and not is_start and bool(val_text)
        fill_color = COLOR_SOLUTION if is_solved_val else COLOR_TEXT_PRIMARY

        text_elem.attrib["x"] = f"{cx:.6f}"
        text_elem.attrib["y"] = f"{cy:.6f}"
        text_elem.attrib["text-anchor"] = "middle"
        text_elem.attrib["dominant-baseline"] = "central"
        text_elem.attrib["style"] = (
            f"font-family:{FONT_FAMILY};font-weight:bold;font-size:{fsize};"
            f"fill:{fill_color};stroke:none;"
        )

        if len(text_elem) > 0:
            tspan = text_elem[0]
            tspan.attrib["x"] = f"{cx:.6f}"
            tspan.attrib["y"] = f"{cy:.6f}"
            tspan.attrib["text-anchor"] = "middle"
            tspan.attrib["dominant-baseline"] = "central"
            tspan.attrib["style"] = (
                f"font-family:{FONT_FAMILY};font-weight:bold;font-size:{fsize};"
                f"fill:{fill_color};text-anchor:middle;dominant-baseline:central;"
            )

        if is_solved_val and rect is not None and raw_parent is not None:
            rect.attrib["style"] = (
                f"fill:{FILL_SOLUTION};stroke:{COLOR_SOLUTION};stroke-width:0.8;"
                "stroke-linejoin:round;stroke-opacity:1"
            )
            # Ensure text is drawn on top of the tinted background rect
            raw_parent.remove(raw_text)
            raw_parent.append(raw_text)

    def _format_operator_element(self, text_elem, op_text: str):
        """Cleanly center and style operator circles with adaptive font sizing."""
        if len(text_elem) > 0:
            text_elem[0].text = str(op_text)
        else:
            text_elem.text = str(op_text)

        raw_text = text_elem.raw_element if hasattr(text_elem, "raw_element") else text_elem
        raw_parent = raw_text.getparent()
        circle = None
        prev = raw_text.getprevious()
        if prev is not None and prev.tag.endswith("circle"):
            circle = prev
        elif (
            raw_parent is not None
            and raw_parent.attrib.get("id") != "layer1"
            and not raw_parent.tag.endswith("svg")
        ):
            circle = raw_parent.find("{http://www.w3.org/2000/svg}circle")

        if circle is not None:
            cx = float(circle.attrib.get("cx", 0))
            cy = float(circle.attrib.get("cy", 0))
        else:
            cx, cy = 144.27673, 126.3138

        for attr in ["transform", "lengthAdjust", "textLength"]:
            text_elem.attrib.pop(attr, None)
        for child in text_elem:
            for attr in ["transform", "lengthAdjust", "textLength"]:
                child.attrib.pop(attr, None)

        fsize = self._calc_operator_font_size(op_text)

        text_elem.attrib["x"] = f"{cx:.6f}"
        text_elem.attrib["y"] = f"{cy:.6f}"
        text_elem.attrib["text-anchor"] = "middle"
        text_elem.attrib["dominant-baseline"] = "central"
        text_elem.attrib["style"] = (
            f"font-family:{FONT_FAMILY};font-weight:bold;font-size:{fsize};"
            f"fill:{COLOR_TEXT_PRIMARY};stroke:none;"
        )

        if len(text_elem) > 0:
            tspan = text_elem[0]
            tspan.attrib["x"] = f"{cx:.6f}"
            tspan.attrib["y"] = f"{cy:.6f}"
            tspan.attrib["text-anchor"] = "middle"
            tspan.attrib["dominant-baseline"] = "central"
            tspan.attrib["style"] = (
                f"font-family:{FONT_FAMILY};font-weight:bold;font-size:{fsize};"
                f"fill:{COLOR_TEXT_PRIMARY};text-anchor:middle;dominant-baseline:central;"
            )

    def _set_footer(self, text: str = DEFAULT_FOOTER_TEXT, visible: bool = True):
        footer = None
        for elem in self.svg.doc.find_all("text"):
            if elem.attrib.get("id") == "Footer":
                footer = elem
                break

        if not visible:
            if footer is not None:
                raw_elem = footer.raw_element if hasattr(footer, "raw_element") else footer
                parent = raw_elem.getparent()
                if parent is not None:
                    parent.remove(raw_elem)
            return

        if footer is None:
            layer = self.svg.doc.find_by_id("layer1") or self.svg.doc.root
            footer_elem = layer.create_child(
                "text",
                attrib={
                    "id": "Footer",
                    "x": str(FOOTER_DEFAULT_X),
                    "y": str(FOOTER_DEFAULT_Y),
                    "style": get_footer_style(),
                },
            )
            footer_elem.create_child(
                "tspan",
                attrib={
                    "id": "FooterSpan",
                    "style": get_footer_style(),
                },
                text=text,
            )
        else:
            footer.attrib["style"] = get_footer_style()
            spans = footer.find_all("tspan")
            if spans:
                spans[0].text = text
                spans[0].attrib["style"] = get_footer_style()
            else:
                footer.text = text


    def create_new_rally(self, algorithm_results, filename_rally, filename_solution):
        solution_copy = RallyTemplate(self.file_name)
        rally_copy = RallyTemplate(self.file_name)

        op_string = operator_to_string(algorithm_results.operations)
        config_text = "Operators: {} - Max Num: {} - Seed: {}".format(
            op_string, algorithm_results.max_value, algorithm_results.seed
        )
        solution_copy.title_tspan_elements[self.CONFIG_SPAN].text = config_text
        rally_copy.title_tspan_elements[self.CONFIG_SPAN].text = config_text

        solution_copy.title_tspan_elements[self.TITLE_SPAN].text = "Math Rally — Lösung"
        rally_copy.title_tspan_elements[self.TITLE_SPAN].text = "Math Rally"

        # Style title spans
        for tmpl in [solution_copy, rally_copy]:
            tmpl.title_tspan_elements[self.TITLE_SPAN].attrib["style"] = get_title_style()
            tmpl.title_tspan_elements[self.CONFIG_SPAN].attrib["style"] = get_subtitle_style()

        # Footer (Student sheet gets Name/Date line, solution does not)
        rally_copy._set_footer(visible=True)
        solution_copy._set_footer(visible=False)


        for i, element in enumerate(algorithm_results.result):
            if i == 0:
                val = str(element[2])
                self._format_value_element(
                    solution_copy.value_elements["value.0"],
                    val,
                    is_solution=True,
                    is_start=True,
                )
                self._format_value_element(
                    rally_copy.value_elements["value.0"],
                    val,
                    is_solution=False,
                    is_start=True,
                )
            else:
                val = str(element[2])
                self._format_value_element(
                    solution_copy.value_elements[f"value.{i}"],
                    val,
                    is_solution=True,
                    is_start=False,
                )
                self._format_value_element(
                    rally_copy.value_elements[f"value.{i}"],
                    "",
                    is_solution=False,
                    is_start=False,
                )

                op_symbol = operator_to_string([element[0]])
                operator_text = f"{op_symbol}{element[1]}"
                self._format_operator_element(
                    solution_copy.operator_elements[f"operatorText.{i - 1}"],
                    operator_text,
                )
                self._format_operator_element(
                    rally_copy.operator_elements[f"operatorText.{i - 1}"],
                    operator_text,
                )

        solution_copy.svg.write(filename_solution)
        rally_copy.svg.write(filename_rally)
