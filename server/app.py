"""
server/app.py — Connexion ASGI application for Multi-Exercise Sheet Editor.
Loads server/openapi.yaml contract-first and maps endpoints to server.api handlers.
"""

from pathlib import Path
import connexion
from starlette.middleware.cors import CORSMiddleware


def create_app() -> connexion.AsyncApp:
    """Creates and configures the Connexion AsyncApp using openapi.yaml."""
    spec_dir = Path(__file__).resolve().parent
    connexion_app = connexion.AsyncApp(__name__, specification_dir=str(spec_dir))

    # Enable CORS for local frontend development
    connexion_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    connexion_app.add_api(
        "openapi.yaml",
        validate_responses=False,
        strict_validation=False,
    )
    return connexion_app


connexion_app = create_app()
app = connexion_app
