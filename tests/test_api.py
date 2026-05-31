"""FastAPI endpoint tests — mock fallback, no API key needed."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


class TestRoot:
    def test_root_returns_200(self):
        assert client.get("/").status_code == 200
    def test_root_contains_placeholder(self):
        assert "AI PR Review" in client.get("/").text


class TestApiDiff:
    def test_returns_200(self):
        assert client.get("/api/diff?owner=test&repo=test&pr=1").status_code == 200

    def test_contains_expected_keys(self):
        data = client.get("/api/diff?owner=test&repo=test&pr=1").json()
        for k in ("pr", "files", "commits", "structured_diff"):
            assert k in data

    def test_diff_files_have_hunks(self):
        data = client.get("/api/diff?owner=test&repo=test&pr=1").json()
        sd = data["structured_diff"]
        assert len(sd["files"]) > 0
        assert "stats" in sd


class TestApiReview:
    def test_returns_200(self):
        assert client.get("/api/review?owner=test&repo=test&pr=1").status_code == 200

    def test_contains_expected_keys(self):
        data = client.get("/api/review?owner=test&repo=test&pr=1").json()
        for k in ("summary", "risk_items", "suggestions", "meta"):
            assert k in data

    def test_risk_items_have_required_fields(self):
        data = client.get("/api/review?owner=test&repo=test&pr=1").json()
        for item in data["risk_items"]:
            assert "file" in item
            assert "severity" in item
