"""
server/composer.py — Multi-exercise A4 sheet composer and block generator.
"""

from pathlib import Path
from random import Random
from typing import Optional, Union, cast
import lxml.etree as ET

from core.operators import Operator
from exercises.addsub.algorithm import AddSubAlgorithm
from exercises.mathrally.algorithm import RallyAlgorithm
from exercises.mathrally.template import RallyTemplate
from exercises.zahlenmauer.algorithm import ZahlenmauerAlgorithm
from exercises.zahlenmauer.difficulty import Difficulty
from exercises.zahlenmauer.template import ZahlenmauerTemplate
from server.models import ExerciseBlockSpec, ExerciseType, SheetSpec
from svg.canvas_template import CanvasExerciseTemplate
from svg.number_paper.written_calc_exercise_box import WrittenCalcExerciseBox
from svg.svg_groups import calculate_group_dimensions
from svg.svg_handler import SvgElement, render_svg_to_pdf


def generate_block_element(
    block: ExerciseBlockSpec,
    is_solution: bool = False,
    exercise_index: int = 1,
) -> tuple[SvgElement, float, float]:
    """
    Generates a standalone SVG group for an exercise block.
    Returns (element, width_in_mm, height_in_mm).
    """
    params = block.params or {}
    seed = params.get("seed")

    if block.type == ExerciseType.ZAHLENMAUER:
        base_size = int(params.get("base_size", 4))
        diff_str = str(params.get("difficulty", "medium")).lower()
        difficulty = Difficulty[diff_str.upper()]
        min_value = int(params.get("min_value", 1))
        max_value = params.get("max_value")
        max_val_int = int(max_value) if max_value is not None else max(100, (2 ** (base_size - 1)) * 10)

        algo = ZahlenmauerAlgorithm(
            base_size=base_size,
            difficulty=difficulty,
            min_value=min_value,
            max_value=max_val_int,
            num_pyramids=1,
            rand_seed=seed,
        )
        puzzles = algo.build()
        zm_template = ZahlenmauerTemplate()
        elem = zm_template._render_pyramid(
            puzzles[0],
            index=exercise_index,
            is_solution=is_solution,
            show_numbering=params.get("show_numbering", True),
        )

    elif block.type == ExerciseType.ADDSUB:
        op_str = str(params.get("operators", "+-"))
        ops = []
        if "+" in op_str:
            ops.append(Operator.ADDITION)
        if "-" in op_str:
            ops.append(Operator.SUBTRACTION)
        if "*" in op_str or "×" in op_str:
            ops.append(Operator.MULTIPLICATION)
        if "/" in op_str or "÷" in op_str:
            ops.append(Operator.DIVISION)
        if not ops:
            ops = [Operator.ADDITION, Operator.SUBTRACTION]

        min_val = int(params.get("min_value", 10))
        max_val = int(params.get("max_value", 999))
        num_rows = int(params.get("num_rows", 2))

        algo_addsub = AddSubAlgorithm(
            operator_list=ops,
            min_value=min_val,
            max_value=max_val,
            num_exercises=1,
            num_rows_per_exercise=num_rows,
            rand_seed=seed,
        )
        algo_addsub.build_addsub()
        op, values = algo_addsub.result[0]

        box = WrittenCalcExerciseBox(
            op,
            values,
            exercise_number=exercise_index if params.get("show_numbering", True) else None,
        )
        elem = box.generateBox()

    elif block.type == ExerciseType.MATHRALLY:
        # Load rally template, inject values, and wrap its exercise layer
        template_name = str(params.get("template", "Rally1.svg"))
        template_path = Path(__file__).parent.parent / "img" / template_name
        if not template_path.exists():
            template_path = Path(__file__).parent.parent / "img" / "Rally1.svg"

        op_str = str(params.get("operators", "+-*/"))
        ops = []
        if "+" in op_str:
            ops.append(Operator.ADDITION)
        if "-" in op_str:
            ops.append(Operator.SUBTRACTION)
        if "*" in op_str or "×" in op_str:
            ops.append(Operator.MULTIPLICATION)
        if "/" in op_str or "÷" in op_str:
            ops.append(Operator.DIVISION)
        if not ops:
            ops = [Operator.ADDITION, Operator.SUBTRACTION, Operator.MULTIPLICATION, Operator.DIVISION]

        rally_tmpl = RallyTemplate(template_path)
        rally_algo = RallyAlgorithm(
            operator_list=ops,
            min_value=int(params.get("min_value", 1)),
            max_value=int(params.get("max_value", 100)),
            num_operators=rally_tmpl.num_operators,
            rand_seed=seed,
        )
        rally_algo.build_rally()

        # Format elements directly inside a cloned document
        cloned_doc = rally_tmpl.doc.clone()
        # Find layer1 or root children
        layer = cloned_doc.find_by_id("layer1") or cloned_doc.root
        elem = SvgElement("g", attrib={"id": f"rally_block_{exercise_index}"})
        for child in layer.iterchildren():
            elem.append(child.clone())

    elif block.type == ExerciseType.CUSTOM_SVG:
        raw_svg = str(params.get("svg_content", "<rect width='40' height='40' fill='#cbd5e1'/>"))
        elem = SvgElement("g", attrib={"id": f"custom_svg_{exercise_index}"})
        try:
            parsed = ET.fromstring(f"<g xmlns='http://www.w3.org/2000/svg'>{raw_svg}</g>")
            for raw_node in list(parsed):
                elem.append(cast(ET._Element, raw_node))
        except Exception:
            elem.append(cast(ET._Element, ET.fromstring("<rect width='40' height='40' fill='#f87171' opacity='0.5'/>")))  # noqa: E501

    else:
        raise ValueError(f"Unknown exercise type: {block.type}")

    # Compute bounding box dimensions
    dims = calculate_group_dimensions(elem)
    width = float(dims.get("width", 50.0))
    height = float(dims.get("height", 30.0))

    return elem, width, height


def compose_sheet(spec: SheetSpec) -> CanvasExerciseTemplate:
    """
    Composes a complete A4 CanvasExerciseTemplate according to the SheetSpec.
    """
    canvas = CanvasExerciseTemplate()

    # Set Header
    title = spec.title or "Mathe-Übungsblatt"
    subtitle = spec.header.subtitle if spec.header else ""
    canvas.set_header(title, subtitle)
    canvas.set_footer(visible=True)

    drawing_group = canvas.drawing_area_group
    if drawing_group is None:
        drawing_group = canvas.doc.root.find_by_id(CanvasExerciseTemplate.DRAWING_AREA_ID)

    if drawing_group is not None:
        for idx, block in enumerate(spec.blocks):
            elem, w, h = generate_block_element(
                block,
                is_solution=spec.show_solutions,
                exercise_index=idx + 1,
            )

            scale = block.scale if block.scale > 0 else 1.0
            transform = f"translate({block.x},{block.y})"
            if scale != 1.0:
                transform += f" scale({scale})"

            wrapper = SvgElement("g", attrib={"id": f"block_{block.id}", "transform": transform})
            wrapper.append(elem)
            drawing_group.append(wrapper)

    return canvas
