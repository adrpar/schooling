from pathlib import Path
from typing import Any, Optional, Sequence, Union

from svg.styles import (
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    DEFAULT_FOOTER_TEXT,
    FONT_FAMILY,
    FONT_SIZE_LABEL,
    FONT_SIZE_SUBTITLE,
    FONT_SIZE_TITLE,
    FOOTER_DEFAULT_X,
    FOOTER_DEFAULT_Y,
    HEADER_TITLE_X,
    HEADER_TITLE_Y,
    HEADER_SUBTITLE_Y,
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
    Handles base SVG document loading, unified header (title & config subtitle),
    footer (student info), and layout packing into the designated drawing area.
    """

    TITLE_ID = "Title"
    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"
    FOOTER_ID = "Footer"
    FOOTER_SPAN = "FooterSpan"
    DRAWING_AREA_ID = "drawingArea"
    DRAWING_AREA_RECT_ID = "drawingAreaRect"

    def __init__(self, template_path: Union[str, Path]):
        self.template_path = Path(template_path)
        self.doc = SvgDocument.from_file(self.template_path)
        self._init_canvas_elements()

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
