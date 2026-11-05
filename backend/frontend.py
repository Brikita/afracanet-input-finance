"""Serve the two built entry points without masking unknown API routes."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


def mount_frontend(app: FastAPI, directory: Path):
    if not directory.is_dir():
        return

    @app.get("/about", include_in_schema=False)
    @app.get("/about/", include_in_schema=False)
    async def product_page():
        return FileResponse(directory / "about.html")

    app.mount("/", StaticFiles(directory=directory, html=True), name="frontend")
