from pathlib import Path
from typing import Any, Optional, Sequence, Union

from svg.styles import (
    COLOR_SOLUTION,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    DEFAULT_FOOTER_TEXT,
    FILL_SOLUTION,
    FONT_FAMILY,
    FONT_SIZE_LABEL,
    FONT_SIZE_SUBTITLE,
    FONT_SIZE_TITLE,
    FOOTER_DEFAULT_X,
    FOOTER_DEFAULT_Y,
    HEADER_TITLE_X,
    HEADER_TITLE_Y,
    HEADER_SUBTITLE_Y,
    PAGE_HEIGHT,
    PAGE_WIDTH,
    get_footer_style,
    get_label_style,
    get_subtitle_style,
    get_title_style,
)
from svg.svg_groups import distribute_groups_in_drawing_area
from svg.svg_handler import SvgDocument, SvgElement


class CanvasExerciseTemplate:
    """
    Reusable base class for canvas-based math exercises (e.g. AddSub, Zahlenmauer).
    Handles base SVG document generation or loading, unified header (title & config subtitle),
    footer (student info), and layout packing into the designated drawing area.
    """

    TITLE_ID = "Title"
    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"
    FOOTER_ID = "Footer"
    FOOTER_SPAN = "FooterSpan"
    DRAWING_AREA_ID = "drawingArea"
    DRAWING_AREA_RECT_ID = "drawingAreaRect"

    # Default drawing area bounding box within A4 page (margins in mm)
    DEFAULT_DRAWING_X = 14.0
    DEFAULT_DRAWING_Y = 32.0
    DEFAULT_DRAWING_WIDTH = 182.0
    DEFAULT_DRAWING_HEIGHT = 244.0

    def __init__(self, template_path: Optional[Union[str, Path]] = None):
        self.template_path = Path(template_path) if template_path else None
        if self.template_path is not None and self.template_path.exists():
            self.doc = SvgDocument.from_file(self.template_path)
        else:
            self.doc = self.create_blank_canvas()
        self._init_canvas_elements()

    @classmethod
    def create_blank_canvas(
        cls,
        width: float = PAGE_WIDTH,
        height: float = PAGE_HEIGHT,
        drawing_x: float = DEFAULT_DRAWING_X,
        drawing_y: float = DEFAULT_DRAWING_Y,
        drawing_width: float = DEFAULT_DRAWING_WIDTH,
        drawing_height: float = DEFAULT_DRAWING_HEIGHT,
    ) -> SvgDocument:
        """
        Dynamically generates a standard A4 worksheet SVG document with drawing area,
        title, configuration subtitle, and footer directly from code.
        """
        raw_svg = (
            f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            f'<svg width="{width:.0f}mm" height="{height:.0f}mm" viewBox="0 0 {width:.0f} {height:.0f}" '
            f'version="1.1" id="svg1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">\n'
            f'  <defs id="defs1" />\n'
            f'  <g id="layer1">\n'
            f'    <g id="{cls.DRAWING_AREA_ID}">\n'
            f'      <rect style="fill:none;stroke:none;" id="{cls.DRAWING_AREA_RECT_ID}" '
            f'width="{drawing_width:.0f}" height="{drawing_height:.0f}" x="{drawing_x:.0f}" y="{drawing_y:.0f}" />\n'
            f'    </g>\n'
            f'    <text xml:space="preserve" style="{get_title_style()}" x="{HEADER_TITLE_X}" y="{HEADER_TITLE_Y}" id="{cls.TITLE_ID}">\n'
            f'      <tspan id="{cls.TITLE_SPAN}" style="{get_title_style()}" x="{HEADER_TITLE_X}" y="{HEADER_TITLE_Y}">Titel</tspan>\n'
            f'      <tspan id="{cls.CONFIG_SPAN}" style="{get_subtitle_style()}" x="{HEADER_TITLE_X}" y="{HEADER_SUBTITLE_Y}">Untertitel</tspan>\n'
            f'    </text>\n'
            f'    <text xml:space="preserve" style="{get_footer_style()}" x="{FOOTER_DEFAULT_X}" y="{FOOTER_DEFAULT_Y}" id="{cls.FOOTER_ID}">\n'
            f'      <tspan id="{cls.FOOTER_SPAN}" style="{get_footer_style()}">{DEFAULT_FOOTER_TEXT}</tspan>\n'
            f'    </text>\n'
            f'  </g>\n'
            f'</svg>'
        )
        return SvgDocument.from_string(raw_svg)

    def _init_canvas_elements(self) -> None:
        """Locates drawing area, title, and footer elements in the document."""
        self.drawing_area_group = self.doc.find_by_id(self.DRAWING_AREA_ID)
        if self.drawing_area_group is not None:
            rect = self.drawing_area_group.find_by_id(self.DRAWING_AREA_RECT_ID)
            if rect is None:
                rects = self.drawing_area_group.find_all("rect")
                rect = rects[0] if rects else None
            self.drawing_area = rect
            if self.drawing_area is not None:
                self.drawing_area.attrib["style"] = "fill:none;stroke:none;"
        else:
            self.drawing_area = None

        self.title_element = self.doc.find_by_id(self.TITLE_ID)
        self.title_tspans: dict[str, SvgElement] = {}
        if self.title_element is not None:
            for span in self.title_element.find_all("tspan"):
                span_id = span.id
                if span_id:
                    self.title_tspans[span_id] = span

        self.footer_element = self.doc.find_by_id(self.FOOTER_ID)
        self.footer_span = (
            self.doc.find_by_id(self.FOOTER_SPAN)
            if self.footer_element is not None
            else None
        )

        self.style_header()

    def style_header(self) -> None:
        """Applies unified typography styles to Title and Config subtitle elements."""
        if self.TITLE_SPAN in self.title_tspans:
            self.title_tspans[self.TITLE_SPAN].attrib["style"] = get_title_style()
        elif self.title_element is not None:
            self.title_element.attrib["style"] = get_title_style()

        if self.CONFIG_SPAN in self.title_tspans:
            self.title_tspans[self.CONFIG_SPAN].attrib["style"] = get_subtitle_style()

    def set_title(self, title: str) -> None:
        """Sets the main exercise title text with standardized styling."""
        if self.TITLE_SPAN in self.title_tspans:
            span = self.title_tspans[self.TITLE_SPAN]
            span.text = title
            span.attrib["style"] = get_title_style()
        elif self.title_element is not None:
            spans = self.title_element.find_all("tspan")
            if spans:
                spans[0].text = title
                spans[0].attrib["style"] = get_title_style()
            else:
                self.title_element.text = title
                self.title_element.attrib["style"] = get_title_style()

    def set_config_text(self, config_text: str) -> None:
        """Sets the configuration subtitle (e.g. operators, seed, difficulty) with standardized styling."""
        if self.CONFIG_SPAN in self.title_tspans:
            span = self.title_tspans[self.CONFIG_SPAN]
            span.text = config_text
            span.attrib["style"] = get_subtitle_style()
        elif self.title_element is not None:
            config_span = self.title_element.create_child(
                "tspan",
                attrib={
                    "id": self.CONFIG_SPAN,
                    "x": str(HEADER_TITLE_X),
                    "y": str(HEADER_SUBTITLE_Y),
                    "style": get_subtitle_style(),
                },
                text=config_text,
            )
            self.title_tspans[self.CONFIG_SPAN] = config_span

    def set_header(self, title: str, config_text: Optional[str] = None) -> None:
        """Convenience method to set title and config subtitle with unified styling."""
        self.set_title(title)
        if config_text:
            self.set_config_text(config_text)

    def set_footer(
        self,
        footer_text: Optional[str] = DEFAULT_FOOTER_TEXT,
        visible: bool = True,
    ) -> None:
        """
        Sets or toggles the worksheet footer (student name & date).
        If visible=False, removes or clears the footer (useful for solution sheets).
        """
        if not visible:
            if self.footer_element is not None:
                raw_elem = self.footer_element.raw_element
                parent = raw_elem.getparent()
                if parent is not None:
                    parent.remove(raw_elem)
                self.footer_element = None
                self.footer_span = None
            return

        text_val = footer_text or DEFAULT_FOOTER_TEXT
        if self.footer_element is None:
            target_container = self.doc.find_by_id("layer1") or self.doc.root
            self.footer_element = target_container.create_child(
                "text",
                attrib={
                    "id": self.FOOTER_ID,
                    "x": str(FOOTER_DEFAULT_X),
                    "y": str(FOOTER_DEFAULT_Y),
                    "style": get_footer_style(),
                },
            )
            self.footer_span = self.footer_element.create_child(
                "tspan",
                attrib={
                    "id": self.FOOTER_SPAN,
                    "style": get_footer_style(),
                },
                text=text_val,
            )
        else:
            self.footer_element.attrib["style"] = get_footer_style()
            if self.footer_span is not None:
                self.footer_span.text = text_val
                self.footer_span.attrib["style"] = get_footer_style()
            else:
                spans = self.footer_element.find_all("tspan")
                if spans:
                    spans[0].text = text_val
                    spans[0].attrib["style"] = get_footer_style()
                    self.footer_span = spans[0]
                else:
                    self.footer_element.text = text_val

    @staticmethod
    def create_exercise_label(
        index: int,
        x: float = 0.0,
        y: float = -2.2,
        prefix: str = "#",
    ) -> SvgElement:
        """
        Builds a standard, unified exercise index label (e.g. '#1', '#2').
        """
        return SvgElement(
            "text",
            attrib={
                "x": f"{x:.2f}",
                "y": f"{y:.2f}",
                "style": get_label_style(),
            },
            text=f"{prefix}{index}",
        )

    def distribute_exercises(
        self, exercise_nodes: Sequence[Union[SvgElement, Any]]
    ) -> None:
        """
        Packs exercise SVG groups into the drawing area in rows.
        """
        if self.drawing_area is not None and self.drawing_area_group is not None:
            distribute_groups_in_drawing_area(
                exercise_nodes,
                self.drawing_area,
                self.drawing_area_group,
            )

    def write(self, file_path: Union[str, Path]) -> None:
        """Writes current document to the specified SVG file path."""
        self.doc.write(file_path)

    def clone(self) -> "CanvasExerciseTemplate":
        """Creates an independent clone of this canvas template."""
        cloned = self.__class__.__new__(self.__class__)
        cloned.template_path = self.template_path
        cloned.doc = self.doc.clone()
        cloned._init_canvas_elements()
        return cloned


def calc_adaptive_font_size(
    text: str,
    max_font_size: float = 6.0,
    min_font_size: float = 3.8,
    length_thresholds: Optional[list[tuple[int, float]]] = None,
) -> float:
    """
    Computes an adaptive font size based on text length to prevent clipping.

    :param text: Text string to measure.
    :param max_font_size: Font size for short text (<=1 character).
    :param min_font_size: Minimum font size for longer numbers.
    :param length_thresholds: Optional list of (max_len, font_size) pairs.
    """
    length = len(str(text))
    if length_thresholds:
        for max_len, size in length_thresholds:
            if length <= max_len:
                return size
        return min_font_size

    if length <= 1:
        return max_font_size
    elif length == 2:
        return max(min_font_size, max_font_size - 0.5)
    elif length == 3:
        return max(min_font_size, max_font_size - 1.5)
    else:
        return min_font_size


def center_text_in_rect(
    text_elem: Any,
    rect_elem: Optional[Any] = None,
    fallback_bounds: Optional[tuple[float, float, float, float]] = None,
) -> tuple[float, float]:
    """
    Centers a <text> element (and its child <tspan>s) precisely inside a bounding <rect>.
    Strips distorting Inkscape attributes (transform, lengthAdjust, textLength) and
    sets x, y, text-anchor='middle', and dominant-baseline='central'.

    :param text_elem: The SVG text element.
    :param rect_elem: Optional SVG rect element to center inside.
    :param fallback_bounds: (x, y, width, height) used if rect_elem is None or lacks attributes.
    :return: Computed center coordinates (cx, cy).
    """
    if rect_elem is not None:
        rx = float(rect_elem.attrib.get("x", fallback_bounds[0] if fallback_bounds else 0.0))
        ry = float(rect_elem.attrib.get("y", fallback_bounds[1] if fallback_bounds else 0.0))
        rw = float(rect_elem.attrib.get("width", fallback_bounds[2] if fallback_bounds else 0.0))
        rh = float(rect_elem.attrib.get("height", fallback_bounds[3] if fallback_bounds else 0.0))
        cx = rx + rw / 2.0
        cy = ry + rh / 2.0
    elif fallback_bounds is not None:
        cx = fallback_bounds[0] + fallback_bounds[2] / 2.0
        cy = fallback_bounds[1] + fallback_bounds[3] / 2.0
    else:
        cx, cy = 0.0, 0.0

    for attr in ["transform", "lengthAdjust", "textLength"]:
        text_elem.attrib.pop(attr, None)
    for child in text_elem:
        for attr in ["transform", "lengthAdjust", "textLength"]:
            child.attrib.pop(attr, None)

    text_elem.attrib["x"] = f"{cx:.6f}"
    text_elem.attrib["y"] = f"{cy:.6f}"
    text_elem.attrib["text-anchor"] = "middle"
    text_elem.attrib["dominant-baseline"] = "central"

    for child in text_elem:
        child.attrib["x"] = f"{cx:.6f}"
        child.attrib["y"] = f"{cy:.6f}"
        child.attrib["text-anchor"] = "middle"
        child.attrib["dominant-baseline"] = "central"

    return cx, cy


def center_text_in_circle(
    text_elem: Any,
    circle_elem: Optional[Any] = None,
    fallback_center: Optional[tuple[float, float]] = None,
) -> tuple[float, float]:
    """
    Centers a <text> element (and its child <tspan>s) precisely inside a <circle>.
    Strips distorting Inkscape attributes (transform, lengthAdjust, textLength) and
    sets x, y, text-anchor='middle', and dominant-baseline='central'.

    :param text_elem: The SVG text element.
    :param circle_elem: Optional SVG circle element to center inside.
    :param fallback_center: (cx, cy) used if circle_elem is None or lacks attributes.
    :return: Computed center coordinates (cx, cy).
    """
    if circle_elem is not None:
        cx = float(circle_elem.attrib.get("cx", fallback_center[0] if fallback_center else 0.0))
        cy = float(circle_elem.attrib.get("cy", fallback_center[1] if fallback_center else 0.0))
    elif fallback_center is not None:
        cx, cy = fallback_center
    else:
        cx, cy = 0.0, 0.0

    for attr in ["transform", "lengthAdjust", "textLength"]:
        text_elem.attrib.pop(attr, None)
    for child in text_elem:
        for attr in ["transform", "lengthAdjust", "textLength"]:
            child.attrib.pop(attr, None)

    text_elem.attrib["x"] = f"{cx:.6f}"
    text_elem.attrib["y"] = f"{cy:.6f}"
    text_elem.attrib["text-anchor"] = "middle"
    text_elem.attrib["dominant-baseline"] = "central"

    for child in text_elem:
        child.attrib["x"] = f"{cx:.6f}"
        child.attrib["y"] = f"{cy:.6f}"
        child.attrib["text-anchor"] = "middle"
        child.attrib["dominant-baseline"] = "central"

    return cx, cy


def highlight_solution_box(
    rect_elem: Any,
    text_elem: Any,
    fill: str = FILL_SOLUTION,
    stroke: str = COLOR_SOLUTION,
    stroke_width: str = "0.8",
) -> None:
    """
    Applies solution highlight colors to a box and ensures the text element
    is drawn on top of the tinted background rect.
    """
    rect_elem.attrib["style"] = (
        f"fill:{fill};stroke:{stroke};stroke-width:{stroke_width};"
        "stroke-linejoin:round;stroke-opacity:1"
    )
    raw_text = text_elem.raw_element if hasattr(text_elem, "raw_element") else text_elem
    raw_parent = raw_text.getparent()
    if raw_parent is not None:
        raw_parent.remove(raw_text)
        raw_parent.append(raw_text)

