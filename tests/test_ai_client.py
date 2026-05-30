"""
AI 客户端 —— 单元测试（基于 Mock 降级模式）。
不依赖真实 DeepSeek API Key，验证 Mock 数据的结构与完整性。
"""

import pytest
from unittest.mock import patch, MagicMock
from src.ai.client import chat_completion, _load_mock


class TestChatCompletionMock:
    """chat_completion — Mock 降级测试（强制无 API Key 场景）"""

    @patch("src.ai.client._get_deepseek_client", return_value=None)
    def test_returns_dict_with_expected_keys(self, _mock):
        result = chat_completion([
            {"role": "system", "content": "You are a code reviewer."},
            {"role": "user", "content": "Review this PR."},
        ])
        assert isinstance(result, dict)
        assert "summary" in result
        assert "risk_items" in result
        assert "suggestions" in result

    @patch("src.ai.client._get_deepseek_client", return_value=None)
    def test_risk_items_have_required_fields(self, _mock):
        result = chat_completion([{"role": "user", "content": "test"}])
        for item in result.get("risk_items", []):
            assert "file" in item
            assert "severity" in item
            assert "description" in item
            assert isinstance(item["file"], str)
            assert isinstance(item["severity"], str)
            assert item["severity"] in ("critical", "high", "medium", "low")

    @patch("src.ai.client._get_deepseek_client", return_value=None)
    def test_suggestions_have_required_fields(self, _mock):
        result = chat_completion([{"role": "user", "content": "test"}])
        for s in result.get("suggestions", []):
            assert "file" in s
            assert "description" in s
            assert isinstance(s["file"], str)
            assert isinstance(s["description"], str)

    @patch("src.ai.client._get_deepseek_client", return_value=None)
    def test_summary_is_non_empty(self, _mock):
        result = chat_completion([{"role": "user", "content": "test"}])
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0

    @patch("src.ai.client._get_deepseek_client", return_value=None)
    def test_meta_has_mock_flag(self, _mock):
        result = chat_completion([{"role": "user", "content": "test"}])
        assert result.get("meta", {}).get("mock") is True


class TestMockCache:
    """验证 Mock 缓存行为"""

    def test_load_mock_returns_same_object_on_second_call(self):
        a = _load_mock()
        b = _load_mock()
        assert a is b  # 同一个引用 = 缓存生效

    def test_load_mock_keys_match(self):
        data = _load_mock()
        assert "summary" in data
        assert "risk_items" in data
        assert "suggestions" in data
        assert "meta" in data


class TestChatCompletionWithMockedClient:
    """chat_completion — 模拟真实 API 调用"""

    @patch("src.ai.client._get_deepseek_client")
    def test_handles_api_exception_gracefully(self, mock_get_client):
        """API 异常时应降级到 Mock 数据"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Network error")
        mock_get_client.return_value = mock_client

        result = chat_completion([{"role": "user", "content": "test"}])
        # 应成功降级，返回 mock 数据结构
        assert "summary" in result
        assert isinstance(result["summary"], str)

    @patch("src.ai.client._get_deepseek_client")
    def test_handles_non_json_response(self, mock_get_client):
        """非 JSON 响应应被优雅处理"""
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "This is not JSON at all"
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[mock_choice]
        )
        mock_get_client.return_value = mock_client

        result = chat_completion([{"role": "user", "content": "test"}])
        # 应退化为 raw summary，不会抛异常
        assert "summary" in result
        assert result.get("meta", {}).get("raw") is True

    @patch("src.ai.client._get_deepseek_client")
    def test_extracts_json_from_markdown_block(self, mock_get_client):
        """JSON 被包裹在 ```json 代码块中时应被正确提取"""
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = '```json\n{"summary": "ok", "risk_items": [], "suggestions": []}\n```'
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[mock_choice]
        )
        mock_get_client.return_value = mock_client

        result = chat_completion([{"role": "user", "content": "test"}])
        assert result["summary"] == "ok"
        assert result["risk_items"] == []
