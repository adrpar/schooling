"""
server/app.py — FastAPI application for Multi-Exercise Sheet Editor.
"""

import os
from pathlib import Path
import tempfile
from typing import Optional
import lxml.etree as ET

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from server.composer import compose_sheet, generate_block_element
from server.db import delete_sheet, get_sheet, list_sheets, save_sheet
from server.models import (
    BlockPreviewRequest,
    BlockPreviewResponse,
    CatalogExerciseItem,
    CatalogExerciseParam,
    ExerciseBlockSpec,
    ExerciseType,
    SheetSpec,
    SheetSummary,
)
from svg.svg_handler import render_svg_to_pdf

app = FastAPI(
    title="Math Trainer Sheet Editor API",
    description="Backend API for interactive multi-exercise sheet composition and PDF export.",
    version="0.1.0",
)

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/catalog", response_model=list[CatalogExerciseItem])
def get_catalog() -> list[CatalogExerciseItem]:
    """Returns available exercise types and their parameter schemas."""
    return [
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


@app.post("/api/blocks/preview", response_model=BlockPreviewResponse)
def preview_block(req: BlockPreviewRequest) -> BlockPreviewResponse:
    """Generates an SVG snippet and dimensions for a single block."""
    block = ExerciseBlockSpec(
        type=req.type,
        params=req.params,
        x=0.0,
        y=0.0,
    )
    if req.seed is not None:
        block.params["seed"] = req.seed

    try:
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
        return BlockPreviewResponse(
            type=req.type,
            svg=svg_xml,
            width=width,
            height=height,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate block preview: {e}")


@app.post("/api/sheet/render")
def render_sheet(spec: SheetSpec) -> Response:
    """Renders the complete A4 sheet and returns the raw SVG document."""
    try:
        canvas = compose_sheet(spec)
        svg_str = canvas.doc.to_string()
        return Response(content=svg_str, media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to render sheet: {e}")


@app.post("/api/sheet/pdf")
def export_pdf(spec: SheetSpec) -> FileResponse:
    """Renders the sheet to SVG, compiles to PDF via Inkscape, and returns the PDF file."""
    try:
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


# --- SQLite Persistence Endpoints ---

@app.get("/api/sheets", response_model=list[SheetSummary])
def get_sheets() -> list[SheetSummary]:
    """Lists all saved sheets in SQLite."""
    return list_sheets()


@app.post("/api/sheets", response_model=SheetSpec)
def create_or_save_sheet(sheet: SheetSpec) -> SheetSpec:
    """Saves a sheet specification to SQLite."""
    try:
        return save_sheet(sheet)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save sheet: {e}")


@app.get("/api/sheets/{sheet_id}", response_model=SheetSpec)
def get_single_sheet(sheet_id: str) -> SheetSpec:
    """Loads a specific sheet specification by ID."""
    sheet = get_sheet(sheet_id)
    if not sheet:
        raise HTTPException(status_code=404, detail=f"Sheet with id '{sheet_id}' not found.")
    return sheet


@app.put("/api/sheets/{sheet_id}", response_model=SheetSpec)
def update_existing_sheet(sheet_id: str, sheet: SheetSpec) -> SheetSpec:
    """Updates an existing sheet."""
    sheet.id = sheet_id
    return save_sheet(sheet)


@app.delete("/api/sheets/{sheet_id}")
def delete_existing_sheet(sheet_id: str) -> dict[str, bool]:
    """Deletes a saved sheet by ID."""
    success = delete_sheet(sheet_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Sheet with id '{sheet_id}' not found.")
    return {"deleted": True}
