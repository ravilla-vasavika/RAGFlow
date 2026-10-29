from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:  # runs the lifespan (DB + FAISS init)
        resp = client.get("/health")
        assert resp.status_code == 200
