"""
AI 审查编排器 — 单元测试。
所有测试 mock 掉 chat_completion，不依赖真实 API。
"""

import pytest
from unittest.mock import patch
from src.ai.reviewer import review_pr_diff, _parse_response
from src.ai.types import ReviewResult, RiskItem, Suggestion


# --- 可复用的 Mock AI 响应 ---
MOCK_RAW = {
    "summary": "This PR adds a config module. Overall clean code.",
    "risk_items": [
        {
            "file": "src/config.py",
            "line_range": "L10-L14",
            "severity": "medium",
            "category": "security",
            "description": "No key validation on load.",
            "code_snippet": "load_dotenv()",
        },
        {
            "file": "src/main.py",
            "line_range": "L6-L8",
            "severity": "low",
            "category": "style",
            "description": "Docstring encoding issue.",
            "code_snippet": "print('hello')",
        },
    ],
    "suggestions": [
        {
            "file": "src/config.py",
            "line_range": "L24-L28",
            "description": "Validate key format.",
            "code_before": "key = os.getenv('KEY', '').strip() or None",
            "code_after": "key = os.getenv('KEY', '').strip()\nif key and not key.startswith('sk-'): raise ValueError('Bad key')",
        },
    ],
    "meta": {"model": "deepseek-chat", "mock": True},
}

MOCK_RAW_NO_RISKS = {
    "summary": "Looks good, nothing to flag.",
    "risk_items": [],
    "suggestions": [],
    "meta": {"model": "deepseek-chat", "mock": True},
}


class TestParseResponse:
    """_parse_response — 防御性解析测试"""

    def test_parses_complete_response(self):
        result = _parse_response(MOCK_RAW, model="deepseek-chat")
        assert isinstance(result, ReviewResult)
        assert len(result.summary) > 0
        assert len(result.risk_items) == 2
        assert len(result.suggestions) == 1

    def test_risk_items_are_typed(self):
        result = _parse_response(MOCK_RAW, model="deepseek-chat")
        for item in result.risk_items:
            assert isinstance(item, RiskItem)
            assert item.severity in ("critical", "high", "medium", "low")

    def test_suggestions_are_typed(self):
        result = _parse_response(MOCK_RAW, model="deepseek-chat")
        for s in result.suggestions:
            assert isinstance(s, Suggestion)
            assert isinstance(s.file, str)
            assert isinstance(s.description, str)

    def test_empty_risk_items_produces_empty_list(self):
        result = _parse_response(MOCK_RAW_NO_RISKS, model="deepseek-chat")
        assert result.risk_items == []
        assert result.overall_risk_level == "none"

    def test_missing_fields_get_defaults(self):
        """缺失字段应使用默认值，不抛异常"""
        result = _parse_response({"summary": "ok"}, model="test-model")
        assert result.summary == "ok"
        assert result.risk_items == []
        assert result.suggestions == []
        assert result.meta == {"model": "test-model"}

    def test_overall_risk_level_critical(self):
        result = _parse_response({
            "summary": "bad",
            "risk_items": [
                {"file": "a.py", "severity": "critical", "category": "bug",
                 "description": "crash", "line_range": "L1", "code_snippet": "x"}
            ],
        }, model="test")
        assert result.overall_risk_level == "critical"

    def test_overall_risk_level_picks_highest(self):
        result = _parse_response({
            "summary": "mixed",
            "risk_items": [
                {"file": "a.py", "severity": "low", "category": "style",
                 "description": "...", "line_range": "L1", "code_snippet": "x"},
                {"file": "b.py", "severity": "high", "category": "bug",
                 "description": "...", "line_range": "L2", "code_snippet": "y"},
                {"file": "c.py", "severity": "medium", "category": "perf",
                 "description": "...", "line_range": "L3", "code_snippet": "z"},
            ],
        }, model="test")
        assert result.overall_risk_level == "high"


class TestReviewPrDiff:
    """review_pr_diff — 编排器集成测试（mock chat_completion）"""

    @patch("src.ai.reviewer.chat_completion")
    def test_returns_review_result(self, mock_chat):
        mock_chat.return_value = MOCK_RAW
        result = review_pr_diff("test", "test", 1)
        assert isinstance(result, ReviewResult)
        assert len(result.summary) > 0
        assert len(result.risk_items) == 2
        assert len(result.suggestions) == 1

    @patch("src.ai.reviewer.chat_completion")
    def test_passes_model_parameter(self, mock_chat):
        mock_chat.return_value = MOCK_RAW
        review_pr_diff("test", "test", 1, model="deepseek-reasoner", temperature=0.5)
        call_kw = mock_chat.call_args[1]
        assert call_kw["model"] == "deepseek-reasoner"
        assert call_kw["temperature"] == 0.5

    @patch("src.ai.reviewer.chat_completion")
    def test_handles_mock_response_no_risks(self, mock_chat):
        mock_chat.return_value = MOCK_RAW_NO_RISKS
        result = review_pr_diff("test", "test", 1)
        assert result.overall_risk_level == "none"
        assert result.risk_items == []

    @patch("src.ai.reviewer.chat_completion")
    def test_result_has_valid_structure(self, mock_chat):
        """验证返回结果可以被 dataclass 正常序列化"""
        from dataclasses import asdict

        mock_chat.return_value = MOCK_RAW
        result = review_pr_diff("test", "test", 1)
        d = asdict(result)
        assert "summary" in d
        assert "risk_items" in d
        assert "suggestions" in d
        assert isinstance(d["risk_items"], list)
        assert isinstance(d["suggestions"], list)
