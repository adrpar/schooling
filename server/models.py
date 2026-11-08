"""
server/models.py — Pydantic schemas for Multi-Exercise Sheet Editor.
"""

from enum import Enum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class ExerciseType(str, Enum):
    ADDSUB = "addsub"
    ZAHLENMAUER = "zahlenmauer"
    MATHRALLY = "mathrally"


class HeaderSpec(BaseModel):
    title: str = "Mathe-Übungsblatt"
    subtitle: str = ""
    show_name_field: bool = True
    show_date_field: bool = True


class ExerciseBlockSpec(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: ExerciseType
    x: float = Field(description="X coordinate on A4 canvas in mm", default=20.0)
    y: float = Field(description="Y coordinate on A4 canvas in mm", default=40.0)
    width: Optional[float] = Field(description="Width in mm", default=None)
    height: Optional[float] = Field(description="Height in mm", default=None)
    scale: float = Field(description="Scale multiplier", default=1.0)
    params: dict[str, Any] = Field(default_factory=dict)


class SheetSpec(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = "Mathe-Übungsblatt"
    header: HeaderSpec = Field(default_factory=HeaderSpec)
    blocks: list[ExerciseBlockSpec] = Field(default_factory=list)
    show_solutions: bool = False
    seed: Optional[int] = None


class SheetSummary(BaseModel):
    id: str
    title: str
    block_count: int
    created_at: str
    updated_at: str


class BlockPreviewRequest(BaseModel):
    type: ExerciseType
    params: dict[str, Any] = Field(default_factory=dict)
    show_solution: bool = False
    seed: Optional[int] = None


class BlockPreviewResponse(BaseModel):
    type: ExerciseType
    svg: str
    width: float
    height: float


class CatalogExerciseParam(BaseModel):
    name: str
    label: str
    type: str  # "int", "string", "select", "bool"
    default: Any
    options: Optional[list[str]] = None
    min: Optional[int] = None
    max: Optional[int] = None
    help: Optional[str] = None


class CatalogExerciseItem(BaseModel):
    type: ExerciseType
    name: str
    description: str
    category: str
    default_params: dict[str, Any]
    params: list[CatalogExerciseParam]
    default_width: float
    default_height: float

