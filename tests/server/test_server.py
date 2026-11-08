"""
tests/server/test_server.py — Integration and unit tests for FastAPI backend and SQLite DB.
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from server.app import app
from server.models import ExerciseBlockSpec, ExerciseType, HeaderSpec, SheetSpec


@pytest.fixture
def client_with_temp_db(monkeypatch):
    """Provides a TestClient using an isolated temporary SQLite database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db_path = f.name

    monkeypatch.setattr("server.db.DEFAULT_DB_PATH", temp_db_path)
    client = TestClient(app)
    yield client

    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)


def test_health_check(client_with_temp_db):
    response = client_with_temp_db.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_catalog(client_with_temp_db):
    response = client_with_temp_db.get("/api/catalog")
    assert response.status_code == 200
    catalog = response.json()
    assert len(catalog) >= 3
    types = [item["type"] for item in catalog]
    assert "zahlenmauer" in types
    assert "addsub" in types
    assert "mathrally" in types


def test_preview_zahlenmauer(client_with_temp_db):
    payload = {
        "type": "zahlenmauer",
        "params": {"base_size": 3, "difficulty": "easy", "seed": 42},
        "show_solution": False,
    }
    response = client_with_temp_db.post("/api/blocks/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "zahlenmauer"
    assert "<svg" in data["svg"]
    assert data["width"] > 0
    assert data["height"] > 0


def test_preview_addsub(client_with_temp_db):
    payload = {
        "type": "addsub",
        "params": {"operators": "+", "num_rows": 2, "seed": 42},
        "show_solution": False,
    }
    response = client_with_temp_db.post("/api/blocks/preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "addsub"
    assert "<svg" in data["svg"]
    assert data["width"] > 0
    assert data["height"] > 0


def test_render_multi_block_sheet(client_with_temp_db):
    sheet = SheetSpec(
        title="Kombiniertes Arbeitsblatt",
        header=HeaderSpec(title="Kombiniertes Arbeitsblatt", subtitle="Klasse 3b"),
        blocks=[
            ExerciseBlockSpec(
                type=ExerciseType.ZAHLENMAUER,
                x=20.0,
                y=40.0,
                params={"base_size": 4, "difficulty": "medium", "seed": 10},
            ),
            ExerciseBlockSpec(
                type=ExerciseType.ADDSUB,
                x=110.0,
                y=40.0,
                params={"operators": "+-", "num_rows": 2, "seed": 20},
            ),
        ],
        show_solutions=False,
    )

    response = client_with_temp_db.post("/api/sheet/render", json=sheet.model_dump())
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    svg_content = response.text
    assert "<svg" in svg_content
    assert "Kombiniertes Arbeitsblatt" in svg_content
    assert "pyramid_1" in svg_content
    assert "exerciseBox" in svg_content


def test_export_pdf(client_with_temp_db):
    sheet = SheetSpec(
        title="Test PDF Sheet",
        blocks=[
            ExerciseBlockSpec(
                type=ExerciseType.ZAHLENMAUER,
                x=20.0,
                y=40.0,
                params={"base_size": 3, "difficulty": "easy", "seed": 5},
            )
        ],
    )
    response = client_with_temp_db.post("/api/sheet/pdf", json=sheet.model_dump())
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_sqlite_sheet_crud(client_with_temp_db):
    # 1. Initially empty
    list_res = client_with_temp_db.get("/api/sheets")
    assert list_res.status_code == 200
    assert list_res.json() == []

    # 2. Save a new sheet
    sheet = SheetSpec(
        id="sheet-123",
        title="Meine Übungen",
        blocks=[
            ExerciseBlockSpec(
                type=ExerciseType.ZAHLENMAUER,
                x=25.0,
                y=45.0,
                params={"base_size": 4},
            )
        ],
    )
    save_res = client_with_temp_db.post("/api/sheets", json=sheet.model_dump())
    assert save_res.status_code == 200
    assert save_res.json()["id"] == "sheet-123"
    assert save_res.json()["title"] == "Meine Übungen"

    # 3. List contains 1 sheet
    list_res2 = client_with_temp_db.get("/api/sheets")
    assert list_res2.status_code == 200
    summaries = list_res2.json()
    assert len(summaries) == 1
    assert summaries[0]["id"] == "sheet-123"
    assert summaries[0]["block_count"] == 1

    # 4. Get by ID
    get_res = client_with_temp_db.get("/api/sheets/sheet-123")
    assert get_res.status_code == 200
    loaded = get_res.json()
    assert loaded["title"] == "Meine Übungen"
    assert len(loaded["blocks"]) == 1

    # 5. Update sheet
    sheet.title = "Meine Übungen (Aktualisiert)"
    put_res = client_with_temp_db.put("/api/sheets/sheet-123", json=sheet.model_dump())
    assert put_res.status_code == 200
    assert put_res.json()["title"] == "Meine Übungen (Aktualisiert)"

    # 6. Delete sheet
    del_res = client_with_temp_db.delete("/api/sheets/sheet-123")
    assert del_res.status_code == 200
    assert del_res.json() == {"deleted": True}

    # 7. Verify deletion
    get_res2 = client_with_temp_db.get("/api/sheets/sheet-123")
    assert get_res2.status_code == 404

