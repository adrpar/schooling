import re


def calculate_group_dimensions(group):
    """
    Recursively calculates the bounding box dimensions of a group element,
    considering nested groups and child elements.

    :param group: lxml element representing the <g> group node.
    :return: Dictionary with 'width' and 'height' of the group.
    """
    if not len(group):
        return {"width": 0, "height": 0}

    min_x, min_y, max_x, max_y = (
        float("inf"),
        float("inf"),
        float("-inf"),
        float("-inf"),
    )
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
            x = group_x + float(element.attrib.get("x", 0))
            y = group_y + float(element.attrib.get("y", 0))
            width = float(element.attrib.get("width", 0))
            height = float(element.attrib.get("height", 0))
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + width)
            max_y = max(max_y, y + height)

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


def distribute_groups_in_drawing_area(group_list, drawing_area, drawing_area_group):
    drawing_box_origin_x = float(drawing_area.attrib["x"])
    drawing_box_origin_y = float(drawing_area.attrib["y"])
    drawing_box_width = float(drawing_area.attrib["width"])
    drawing_box_height = float(drawing_area.attrib["height"])

    current_x, current_y = drawing_box_origin_x, drawing_box_origin_y
    row_spacing = 10
    row_height = 0
    row_elements = []

    for exercise in group_list:
        bbox = calculate_group_dimensions(exercise)
        g_width = float(bbox["width"])
        g_height = float(bbox["height"])

        # Move to next row if width exceeds limit
        if current_x + g_width > drawing_box_origin_x + drawing_box_width:
            # Calculate dynamic padding
            total_width = sum(
                float(calculate_group_dimensions(e)["width"]) for e in row_elements
            )
            space_remaining = drawing_box_width - total_width
            padding = (
                space_remaining / (len(row_elements) - 1)
                if len(row_elements) > 1
                else 0
            )

            # Adjust positions in the row
            x_offset = drawing_box_origin_x
            for elem in row_elements:
                bbox = calculate_group_dimensions(elem)
                elem.attrib["transform"] = f"translate({x_offset},{current_y})"
                x_offset += bbox["width"] + padding

                drawing_area_group.append(elem)

            # Reset for new row
            current_x = drawing_box_origin_x
            current_y += row_height + row_spacing
            row_height = 0
            row_elements = []

        # If exceeds drawing height, stop placing
        if current_y + g_height > drawing_box_origin_y + drawing_box_height:
            break

        # Store element in row list
        row_elements.append(exercise)

        # Update cursor position
        current_x += g_width
        row_height = max(row_height, g_height)

    # Final row adjustment
    if row_elements:
        total_width = sum(
            float(calculate_group_dimensions(e)["width"]) for e in row_elements
        )
        space_remaining = drawing_box_width - total_width
        padding = (
            space_remaining / (len(row_elements) - 1) if len(row_elements) > 1 else 0
        )

        x_offset = drawing_box_origin_x
        for elem in row_elements:
            bbox = calculate_group_dimensions(elem)
            elem.attrib["transform"] = f"translate({x_offset},{current_y})"
            x_offset += bbox["width"] + padding

            drawing_area_group.append(elem)
