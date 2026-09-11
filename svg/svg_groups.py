import logging
import re

logger = logging.getLogger(__name__)


def _element_bbox(element, offset_x=0.0, offset_y=0.0):
    """
    Returns (min_x, min_y, max_x, max_y) for a single non-group SVG element,
    relative to the given offset. Handles rect, line, circle, ellipse, and
    falls back to x/y/width/height for unknown elements. (Q27)
    """
    tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

    if tag == "line":
        x1 = float(element.attrib.get("x1", 0))
        y1 = float(element.attrib.get("y1", 0))
        x2 = float(element.attrib.get("x2", 0))
        y2 = float(element.attrib.get("y2", 0))
        return (
            offset_x + min(x1, x2),
            offset_y + min(y1, y2),
            offset_x + max(x1, x2),
            offset_y + max(y1, y2),
        )
    elif tag == "circle":
        cx = float(element.attrib.get("cx", 0))
        cy = float(element.attrib.get("cy", 0))
        r = float(element.attrib.get("r", 0))
        return (offset_x + cx - r, offset_y + cy - r, offset_x + cx + r, offset_y + cy + r)
    elif tag == "ellipse":
        cx = float(element.attrib.get("cx", 0))
        cy = float(element.attrib.get("cy", 0))
        rx = float(element.attrib.get("rx", 0))
        ry = float(element.attrib.get("ry", 0))
        return (offset_x + cx - rx, offset_y + cy - ry, offset_x + cx + rx, offset_y + cy + ry)
    else:
        # rect, text, image, and unknowns
        x = offset_x + float(element.attrib.get("x", 0))
        y = offset_y + float(element.attrib.get("y", 0))
        w = float(element.attrib.get("width", 0))
        h = float(element.attrib.get("height", 0))
        return (x, y, x + w, y + h)


def calculate_group_dimensions(group):
    """
    Recursively calculates the bounding box dimensions of a group element,
    considering nested groups and child elements.

    :param group: lxml element representing the <g> group node.
    :return: Dictionary with 'width' and 'height' of the group.
    """
    if not len(group):
        return {"width": 0, "height": 0}

    min_x, min_y, max_x, max_y = float("inf"), float("inf"), float("-inf"), float("-inf")
    group_x, group_y = parse_transform(group.get("transform"))

    for element in group.iterchildren():
        if element.tag.endswith("g"):
            dims = calculate_group_dimensions(element)
            child_x, child_y = parse_transform(element.attrib.get("transform"))
            x = group_x + child_x
            y = group_y + child_y
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + dims["width"])
            max_y = max(max_y, y + dims["height"])
        else:
            ex1, ey1, ex2, ey2 = _element_bbox(element, group_x, group_y)
            min_x = min(min_x, ex1)
            min_y = min(min_y, ey1)
            max_x = max(max_x, ex2)
            max_y = max(max_y, ey2)

    return {
        "width": max_x - min_x if max_x > min_x else 0,
        "height": max_y - min_y if max_y > min_y else 0,
    }


def parse_transform(transform):
    """Extracts translation values from the transform attribute."""
    if transform:
        match = re.search(r"translate\(([-\d.]+)[, ]*([-\d.]+)?\)", transform)
        if match:
            x = float(match.group(1))
            y = float(match.group(2)) if match.group(2) else 0
            return x, y
    return 0, 0


def _flush_row(
    row_elements,
    row_bboxes,
    current_y,
    drawing_box_origin_x,
    drawing_box_width,
    drawing_area_group,
    center_single: bool = True,
    max_gap: float = None,
):
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
    group_list,
    drawing_area,
    drawing_area_group,
    row_spacing: float = 10.0,
    center_single: bool = True,
    max_gap: float = None,
    center_vertical: bool = False,
):
    drawing_box_origin_x = float(drawing_area.attrib["x"])
    drawing_box_origin_y = float(drawing_area.attrib["y"])
    drawing_box_width = float(drawing_area.attrib["width"])
    drawing_box_height = float(drawing_area.attrib["height"])

    current_x = drawing_box_origin_x
    current_y = drawing_box_origin_y
    row_height = 0.0
    row_elements = []
    row_bboxes = []  # list of (element, width, height)

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
            logger.warning(
                "distribute_groups_in_drawing_area: %d exercise(s) did not fit and were dropped.",
                len(group_list) - len(row_elements) - sum(1 for _ in drawing_area_group),
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
