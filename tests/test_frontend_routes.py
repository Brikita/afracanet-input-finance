"""Production links must reach the right entry point without a blanket SPA fallback."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.frontend import mount_frontend


def test_built_product_routes_and_missing_api(tmp_path):
    (tmp_path / "index.html").write_text("input workspace", encoding="utf-8")
    (tmp_path / "about.html").write_text("product explanation", encoding="utf-8")
    app = FastAPI()
    mount_frontend(app, tmp_path)
    with TestClient(app) as client:
        assert client.get("/").text == "input workspace"
        for path in ("/about", "/about/", "/about.html"):
            response = client.get(path)
            assert response.status_code == 200
            assert response.text == "product explanation"
        assert client.get("/api/unknown-endpoint").status_code == 404
        assert client.get("/missing-asset.js").status_code == 404
