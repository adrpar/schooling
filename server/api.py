"""
server/api.py — Connexion operationId handler implementations.
"""

from pathlib import Path
import tempfile
from typing import Any

from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, Response

from server.composer import compose_sheet, generate_block_element
from server.db import delete_sheet, get_sheet, list_sheets, save_sheet
from server.models import (
    BlockPreviewRequest,
    CatalogExerciseItem,
    CatalogExerciseParam,
    ExerciseBlockSpec,
    ExerciseType,
    SheetSpec,
)
from svg.svg_handler import render_svg_to_pdf


async def health_check() -> dict[str, str]:
    return {"status": "ok"}


async def get_catalog() -> list[dict[str, Any]]:
    """Returns catalog of supported exercises and parameter specifications."""
    items = [
        CatalogExerciseItem(
            type=ExerciseType.ZAHLENMAUER,
            name="Zahlenmauer",
            description="Addition pyramid where each brick is the sum of the two below it.",
            category="Arithmetic Puzzles",
            default_params={
                "base_size": 4,
                "difficulty": "medium",
                "min_value": 1,
                "max_value": 100,
                "show_numbering": True,
            },
            params=[
                CatalogExerciseParam(
                    name="base_size",
                    label="Base Size (Steine)",
                    type="int",
                    default=4,
                    min=3,
                    max=10,
                    help="Number of bricks in the base row (3–10).",
                ),
                CatalogExerciseParam(
                    name="difficulty",
                    label="Difficulty",
                    type="select",
                    default="medium",
                    options=["easy", "medium", "hard"],
                    help="Clue density: easy (pure addition), medium (subtractions), hard (minimal clues).",
                ),
                CatalogExerciseParam(
                    name="min_value",
                    label="Min Value",
                    type="int",
                    default=1,
                    min=1,
                    max=100,
                ),
                CatalogExerciseParam(
                    name="max_value",
                    label="Max Value",
                    type="int",
                    default=100,
                    min=10,
                    max=10000,
                ),
                CatalogExerciseParam(
                    name="show_numbering",
                    label="Show Exercise Number",
                    type="bool",
                    default=True,
                ),
            ],
            default_width=70.0,
            default_height=45.0,
        ),
        CatalogExerciseItem(
            type=ExerciseType.ADDSUB,
            name="Written Calculation (Add/Sub)",
            description="Column-form written arithmetic on simulated math grid paper.",
            category="Written Arithmetic",
            default_params={
                "operators": "+-",
                "num_rows": 2,
                "min_value": 10,
                "max_value": 999,
                "show_numbering": True,
            },
            params=[
                CatalogExerciseParam(
                    name="operators",
                    label="Operators",
                    type="select",
                    default="+-",
                    options=["+", "-", "+-", "+-*", "+-*/"],
                    help="Allowed operations.",
                ),
                CatalogExerciseParam(
                    name="num_rows",
                    label="Operand Rows",
                    type="int",
                    default=2,
                    min=2,
                    max=5,
                    help="Number of numbers added/subtracted.",
                ),
                CatalogExerciseParam(
                    name="min_value",
                    label="Min Value",
                    type="int",
                    default=10,
                    min=1,
                    max=1000,
                ),
                CatalogExerciseParam(
                    name="max_value",
                    label="Max Value",
                    type="int",
                    default=999,
                    min=10,
                    max=99999,
                ),
                CatalogExerciseParam(
                    name="show_numbering",
                    label="Show Exercise Number",
                    type="bool",
                    default=True,
                ),
            ],
            default_width=35.0,
            default_height=30.0,
        ),
        CatalogExerciseItem(
            type=ExerciseType.MATHRALLY,
            name="Math Rally",
            description="Continuous step-by-step arithmetic calculation trail.",
            category="Mental Arithmetic",
            default_params={
                "operators": "+-*/",
                "min_value": 1,
                "max_value": 100,
                "template": "Rally1.svg",
            },
            params=[
                CatalogExerciseParam(
                    name="operators",
                    label="Operators",
                    type="select",
                    default="+-*/",
                    options=["+-", "+*", "+-*/"],
                ),
                CatalogExerciseParam(
                    name="min_value",
                    label="Min Value",
                    type="int",
                    default=1,
                    min=1,
                    max=50,
                ),
                CatalogExerciseParam(
                    name="max_value",
                    label="Max Value",
                    type="int",
                    default=100,
                    min=10,
                    max=1000,
                ),
                CatalogExerciseParam(
                    name="template",
                    label="Visual Template",
                    type="select",
                    default="Rally1.svg",
                    options=["Rally1.svg", "Rally2.svg"],
                ),
            ],
            default_width=180.0,
            default_height=200.0,
        ),
    ]
    return [item.model_dump() for item in items]


async def preview_block(body: dict[str, Any]) -> dict[str, Any]:
    """Generates an SVG snippet and dimensions for a single block."""
    try:
        req = BlockPreviewRequest.model_validate(body)
        block = ExerciseBlockSpec(
            type=req.type,
            params=req.params,
            x=0.0,
            y=0.0,
        )
        if req.seed is not None:
            block.params["seed"] = req.seed

        elem, width, height = generate_block_element(
            block,
            is_solution=req.show_solution,
            exercise_index=1,
        )
        raw_xml = elem.to_string()
        svg_xml = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.1f} {height:.1f}" '
            f'width="{width:.1f}mm" height="{height:.1f}mm">{raw_xml}</svg>'
        )
        return {
            "type": req.type.value,
            "svg": svg_xml,
            "width": width,
            "height": height,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate preview: {e}")


async def render_sheet(body: dict[str, Any]) -> Response:
    """Renders the full A4 worksheet to SVG."""
    try:
        spec = SheetSpec.model_validate(body)
        canvas = compose_sheet(spec)
        svg_str = canvas.doc.to_string()
        return Response(content=svg_str, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to render sheet: {e}")


async def export_pdf(body: dict[str, Any]) -> FileResponse:
    """Renders the worksheet and compiles to PDF via Inkscape."""
    try:
        spec = SheetSpec.model_validate(body)
        canvas = compose_sheet(spec)

        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as temp_svg:
            temp_svg_path = temp_svg.name
            canvas.write(temp_svg_path)

        temp_pdf_path = temp_svg_path.replace(".svg", ".pdf")
        render_svg_to_pdf(temp_svg_path, temp_pdf_path)

        filename = f"{spec.title.lower().replace(' ', '_')}.pdf"
        return FileResponse(
            temp_pdf_path,
            media_type="application/pdf",
            filename=filename,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export PDF: {e}")


# --- SQLite Persistence ---

async def list_saved_sheets() -> list[dict[str, Any]]:
    return [s.model_dump() for s in list_sheets()]


async def save_new_sheet(body: dict[str, Any]) -> dict[str, Any]:
    try:
        spec = SheetSpec.model_validate(body)
        saved = save_sheet(spec)
        return saved.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save sheet: {e}")


async def get_sheet_by_id(sheet_id: str) -> dict[str, Any]:
    sheet = get_sheet(sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail=f"Sheet with id '{sheet_id}' not found.")
    return sheet.model_dump()


async def update_saved_sheet(sheet_id: str, body: dict[str, Any]) -> dict[str, Any]:
    try:
        spec = SheetSpec.model_validate(body)
        spec.id = sheet_id
        saved = save_sheet(spec)
        return saved.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update sheet: {e}")


async def delete_sheet_by_id(sheet_id: str) -> dict[str, bool]:
    success = delete_sheet(sheet_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Sheet with id '{sheet_id}' not found.")
    return {"deleted": True}

