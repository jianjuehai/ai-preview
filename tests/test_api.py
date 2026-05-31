"""
FastAPI 集成测试 — 验证 API 端点返回正确的 JSON 结构。
使用 TestClient，不依赖真实 API Key（Mock 降级）。
"""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)


class TestRootEndpoint:
    """GET / — 占位页面"""

    def test_root_returns_200(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_root_contains_placeholder_content(self):
        resp = client.get("/")
        assert "AI PR Review" in resp.text
        assert "Dashboard is under development" in resp.text


class TestApiDiff:
    """GET /api/diff — Diff 数据端点"""

    def test_diff_returns_200(self):
        resp = client.get("/api/diff?owner=test&repo=test&pr=1")
        assert resp.status_code == 200

    def test_diff_contains_expected_keys(self):
        resp = client.get("/api/diff?owner=test&repo=test&pr=1")
        data = resp.json()
        assert "pr" in data
        assert "files" in data
        assert "commits" in data
        assert "structured_diff" in data

    def test_diff_pr_has_required_fields(self):
        resp = client.get("/api/diff?owner=test&repo=test&pr=1")
        pr = resp.json()["pr"]
        assert "number" in pr
        assert "title" in pr
        assert "state" in pr

    def test_diff_structured_diff_has_stats(self):
        resp = client.get("/api/diff?owner=test&repo=test&pr=1")
        sd = resp.json()["structured_diff"]
        assert "files" in sd
        assert "stats" in sd
        assert "files_changed" in sd["stats"]


class TestApiReview:
    """GET /api/review — AI 审查端点"""

    def test_review_returns_200(self):
        resp = client.get("/api/review?owner=test&repo=test&pr=1")
        assert resp.status_code == 200

    def test_review_contains_expected_keys(self):
        resp = client.get("/api/review?owner=test&repo=test&pr=1")
        data = resp.json()
        assert "summary" in data
        assert "risk_items" in data
        assert "suggestions" in data
        assert "meta" in data

    def test_review_risk_items_have_required_fields(self):
        resp = client.get("/api/review?owner=test&repo=test&pr=1")
        for item in resp.json()["risk_items"]:
            assert "file" in item
            assert "severity" in item
            assert "description" in item

    def test_review_summary_is_non_empty(self):
        resp = client.get("/api/review?owner=test&repo=test&pr=1")
        assert len(resp.json()["summary"]) > 0


class TestCORS:
    """CORS 头验证"""

    def test_cors_header_present(self):
        resp = client.options("/api/diff?owner=test&repo=test&pr=1")
        # TestClient may not set Origin header by default, check GET response
        resp = client.get("/api/review?owner=test&repo=test&pr=1",
                          headers={"Origin": "http://localhost:5173"})
        assert "access-control-allow-origin" in resp.headers
