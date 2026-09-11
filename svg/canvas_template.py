from pathlib import Path
from typing import Any, Optional, Sequence, Union

from svg.svg_groups import distribute_groups_in_drawing_area
from svg.svg_handler import SvgDocument, SvgElement


class CanvasExerciseTemplate:
    """
    Reusable base class for canvas-based math exercises (e.g. AddSub, Zahlenmauer).
    Handles base SVG document loading, title/config updates, and layout packing
    into the designated drawing area.
    """

    TITLE_ID = "Title"
    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"
    DRAWING_AREA_ID = "drawingArea"
    DRAWING_AREA_RECT_ID = "drawingAreaRect"

    def __init__(self, template_path: Union[str, Path]):
        self.template_path = Path(template_path)
        self.doc = SvgDocument.from_file(self.template_path)
        self._init_canvas_elements()

    def _init_canvas_elements(self) -> None:
        """Locates drawing area and title text elements in the document."""
        self.drawing_area_group = self.doc.find_by_id(self.DRAWING_AREA_ID)
        if self.drawing_area_group is not None:
            rect = self.drawing_area_group.find_by_id(self.DRAWING_AREA_RECT_ID)
            if rect is None:
                rects = self.drawing_area_group.find_all("rect")
                rect = rects[0] if rects else None
            self.drawing_area = rect
        else:
            self.drawing_area = None

        self.title_element = self.doc.find_by_id(self.TITLE_ID)
        self.title_tspans: dict[str, SvgElement] = {}
        if self.title_element is not None:
            for span in self.title_element.find_all("tspan"):
                span_id = span.id
                if span_id:
                    self.title_tspans[span_id] = span

    def set_title(self, title: str) -> None:
        """Sets the main exercise title text."""
        if self.TITLE_SPAN in self.title_tspans:
            self.title_tspans[self.TITLE_SPAN].text = title
        elif self.title_element is not None:
            spans = self.title_element.find_all("tspan")
            if spans:
                spans[0].text = title
            else:
                self.title_element.text = title

    def set_config_text(self, config_text: str) -> None:
        """Sets the configuration subtitle (e.g. operators, seed, difficulty)."""
        if self.CONFIG_SPAN in self.title_tspans:
            self.title_tspans[self.CONFIG_SPAN].text = config_text

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
