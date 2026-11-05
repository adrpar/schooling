import logging
import math
import re
from typing import Any, Optional
import lxml.etree as ET
from inkex.transforms import Transform

logger = logging.getLogger(__name__)


def _primitive_bbox(
    element: Any, transform: Transform
) -> tuple[float, float, float, float]:
    """
    Returns (min_x, min_y, max_x, max_y) for a single non-group SVG element
    transformed by the given affine transform. Handles rect, line, circle,
    ellipse, polygon, polyline, and falls back to x/y/width/height for unknown elements.
    """
    tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

    if tag == "line":
        x1 = float(element.attrib.get("x1", 0))
        y1 = float(element.attrib.get("y1", 0))
        x2 = float(element.attrib.get("x2", 0))
        y2 = float(element.attrib.get("y2", 0))
        p1 = transform.apply_to_point((x1, y1))
        p2 = transform.apply_to_point((x2, y2))
        return (min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y))

    elif tag in ("circle", "ellipse"):
        cx = float(element.attrib.get("cx", 0))
        cy = float(element.attrib.get("cy", 0))
        rx = float(element.attrib.get("r" if tag == "circle" else "rx", 0))
        ry = float(element.attrib.get("r" if tag == "circle" else "ry", 0))
        center = transform.apply_to_point((cx, cy))
        half_w = math.hypot(transform.a * rx, transform.c * ry)
        half_h = math.hypot(transform.b * rx, transform.d * ry)
        return (
            center.x - half_w,
            center.y - half_h,
            center.x + half_w,
            center.y + half_h,
        )

    elif tag in ("polygon", "polyline"):
        pts_str = element.attrib.get("points", "").strip()
        if pts_str:
            coords = [float(val) for val in re.split(r"[\s,]+", pts_str) if val]
            pts = [
                transform.apply_to_point((coords[i], coords[i + 1]))
                for i in range(0, len(coords) - 1, 2)
            ]
            if pts:
                xs = [p.x for p in pts]
                ys = [p.y for p in pts]
                return (min(xs), min(ys), max(xs), max(ys))
        return (0.0, 0.0, 0.0, 0.0)

    else:
        # rect, text, image, and generic bounding boxes
        x = float(element.attrib.get("x", 0))
        y = float(element.attrib.get("y", 0))
        w = float(element.attrib.get("width", 0))
        h = float(element.attrib.get("height", 0))
        c1 = transform.apply_to_point((x, y))
        c2 = transform.apply_to_point((x + w, y))
        c3 = transform.apply_to_point((x + w, y + h))
        c4 = transform.apply_to_point((x, y + h))
        xs = [c1.x, c2.x, c3.x, c4.x]
        ys = [c1.y, c2.y, c3.y, c4.y]
        return (min(xs), min(ys), max(xs), max(ys))


def calculate_group_dimensions(group: Any) -> dict[str, float]:
    """
    Recursively calculates the bounding box dimensions of a group element,
    considering nested groups, child elements, and SVG affine transforms
    (translate, rotate, scale, matrix, skew).

    :param group: lxml element representing the <g> group node.
    :return: Dictionary with 'width' and 'height' of the group.
    """
    if not len(group):
        return {"width": 0.0, "height": 0.0}

    bounds = [float("inf"), float("inf"), float("-inf"), float("-inf")]
    initial_transform = Transform(group.get("transform"))

    def _traverse(node: Any, current_transform: Transform) -> None:
        for child in node.iterchildren():
            child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            child_transform = current_transform
            if "transform" in child.attrib:
                child_transform = child_transform @ Transform(child.attrib["transform"])

            if child_tag == "g":
                _traverse(child, child_transform)
            else:
                x1, y1, x2, y2 = _primitive_bbox(child, child_transform)
                bounds[0] = min(bounds[0], x1)
                bounds[1] = min(bounds[1], y1)
                bounds[2] = max(bounds[2], x2)
                bounds[3] = max(bounds[3], y2)

    _traverse(group, initial_transform)

    if bounds[0] == float("inf"):
        return {"width": 0.0, "height": 0.0}

    width = max(0.0, bounds[2] - bounds[0])
    height = max(0.0, bounds[3] - bounds[1])
    return {
        "width": width,
        "height": height,
    }


def parse_transform(transform: Optional[str]) -> tuple[float, float]:
    """
    Extracts translation (x, y) values from any transform attribute,
    supporting translate, matrix, and composite transforms.
    """
    if transform:
        try:
            t = Transform(transform)
            return float(t.e), float(t.f)
        except Exception:
            match = re.search(r"translate\(([-\d.]+)[, ]*([-\d.]+)?\)", transform)
            if match:
                x = float(match.group(1))
                y = float(match.group(2)) if match.group(2) else 0.0
                return x, y
    return 0.0, 0.0


def _flush_row(
    row_elements: list[Any],
    row_bboxes: list[tuple[Any, float, float]],
    current_y: float,
    drawing_box_origin_x: float,
    drawing_box_width: float,
    drawing_area_group: Any,
    center_single: bool = True,
    max_gap: Optional[float] = None,
) -> None:
    """
    Spaces and appends a completed row of elements to the drawing area group.
    - Single elements are centered horizontally by default.
    - Multi-element rows are justified, with an optional max_gap cap to prevent extreme voids.
    """
    total_width = sum(w for _, w, _ in row_bboxes)
    space_remaining = drawing_box_width - total_width
    n = len(row_elements)

    if n == 1:
        x_offset = (
            drawing_box_origin_x + space_remaining / 2.0
            if center_single
            else drawing_box_origin_x
        )
        padding = 0.0
    else:
        natural_gap = space_remaining / (n - 1)
        if max_gap is not None and natural_gap > max_gap:
            padding = max_gap
            cluster_width = total_width + (n - 1) * padding
            x_offset = drawing_box_origin_x + (drawing_box_width - cluster_width) / 2.0
        else:
            padding = natural_gap
            x_offset = drawing_box_origin_x

    for elem, (_, w, _) in zip(row_elements, row_bboxes):
        elem.attrib["transform"] = f"translate({x_offset},{current_y})"
        x_offset += w + padding
        drawing_area_group.append(elem)


def distribute_groups_in_drawing_area(
    group_list: list[Any],
    drawing_area: Any,
    drawing_area_group: Any,
    row_spacing: float = 10.0,
    center_single: bool = True,
    max_gap: Optional[float] = None,
    center_vertical: bool = False,
) -> None:
    """
    Arranges a sequence of group elements in the designated drawing area, wrapping
    rows as needed.
    """
    drawing_box_origin_x = float(drawing_area.attrib["x"])
    drawing_box_origin_y = float(drawing_area.attrib["y"])
    drawing_box_width = float(drawing_area.attrib["width"])
    drawing_box_height = float(drawing_area.attrib["height"])

    current_x = drawing_box_origin_x
    current_y = drawing_box_origin_y
    row_height = 0.0
    row_elements: list[Any] = []
    row_bboxes: list[tuple[Any, float, float]] = []

    for exercise in group_list:
        dims = calculate_group_dimensions(exercise)
        g_width = float(dims["width"])
        g_height = float(dims["height"])

        # Move to next row if width exceeds limit
        if current_x + g_width > drawing_box_origin_x + drawing_box_width and row_elements:
            _flush_row(
                row_elements,
                row_bboxes,
                current_y,
                drawing_box_origin_x,
                drawing_box_width,
                drawing_area_group,
                center_single=center_single,
                max_gap=max_gap,
            )
            current_x = drawing_box_origin_x
            current_y += row_height + row_spacing
            row_height = 0.0
            row_elements = []
            row_bboxes = []

        # If exceeds drawing height, stop placing
        if current_y + g_height > drawing_box_origin_y + drawing_box_height:
            placed_count = sum(1 for _ in drawing_area_group) + len(row_elements)
            dropped = len(group_list) - placed_count
            if dropped > 0:
                logger.warning(
                    "distribute_groups_in_drawing_area: %d exercise(s) did not fit and were dropped.",
                    dropped,
                )
            break

        row_elements.append(exercise)
        row_bboxes.append((exercise, g_width, g_height))
        current_x += g_width
        row_height = max(row_height, g_height)

    # Final row
    if row_elements:
        _flush_row(
            row_elements,
            row_bboxes,
            current_y,
            drawing_box_origin_x,
            drawing_box_width,
            drawing_area_group,
            center_single=center_single,
            max_gap=max_gap,
        )
