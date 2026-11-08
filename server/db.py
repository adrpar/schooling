"""
server/db.py — SQLite persistence for Multi-Exercise Sheet Editor.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
from typing import Optional

from server.models import SheetSpec, SheetSummary

DEFAULT_DB_PATH = os.environ.get(
    "MATH_TRAINER_DB_PATH",
    str(Path(__file__).parent.parent / "sheets.db"),
)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes the SQLite schema if not already present."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sheets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                spec_json TEXT NOT NULL
            );
            """
        )
        conn.commit()


def save_sheet(sheet: SheetSpec, db_path: Optional[str] = None) -> SheetSpec:
    """Creates or updates a sheet specification in SQLite."""
    init_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    spec_json = json.dumps(sheet.model_dump())

    with get_connection(db_path) as conn:
        cursor = conn.execute("SELECT created_at FROM sheets WHERE id = ?", (sheet.id,))
        row = cursor.fetchone()
        created_at = row["created_at"] if row else now

        conn.execute(
            """
            INSERT INTO sheets (id, title, created_at, updated_at, spec_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                updated_at = excluded.updated_at,
                spec_json = excluded.spec_json;
            """,
            (sheet.id, sheet.title, created_at, now, spec_json),
        )
        conn.commit()

    return sheet


def get_sheet(sheet_id: str, db_path: Optional[str] = None) -> Optional[SheetSpec]:
    """Retrieves a SheetSpec by its ID."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute("SELECT spec_json FROM sheets WHERE id = ?", (sheet_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = json.loads(row["spec_json"])
        return SheetSpec.model_validate(data)


def list_sheets(db_path: Optional[str] = None) -> list[SheetSummary]:
    """Returns a list of all saved sheets ordered by most recently updated."""
    init_db(db_path)
    summaries: list[SheetSummary] = []
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "SELECT id, title, created_at, updated_at, spec_json FROM sheets ORDER BY updated_at DESC"
        )
        for row in cursor.fetchall():
            try:
                spec = json.loads(row["spec_json"])
                block_count = len(spec.get("blocks", []))
            except Exception:
                block_count = 0
            summaries.append(
                SheetSummary(
                    id=row["id"],
                    title=row["title"],
                    block_count=block_count,
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
    return summaries


def delete_sheet(sheet_id: str, db_path: Optional[str] = None) -> bool:
    """Deletes a sheet by ID. Returns True if a sheet was deleted."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM sheets WHERE id = ?", (sheet_id,))
        conn.commit()
        return cursor.rowcount > 0

