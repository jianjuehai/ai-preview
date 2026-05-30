"""
CLI 审查模式 — 集成测试。
使用 Click CliRunner + mock review_pr_diff，不依赖真实 API。
"""

import pytest
from unittest.mock import patch
from click.testing import CliRunner
from src.main import cli
from src.ai.types import ReviewResult, RiskItem, Suggestion


# --- Mock 审查结果 ---
def _make_mock_result():
    return ReviewResult(
        summary="Test summary.",
        risk_items=[
            RiskItem(
                file="a.py", line_range="L1-L2", severity="high",
                category="bug", description="Bad bug", code_snippet="x=1"
            ),
        ],
        suggestions=[
            Suggestion(
                file="a.py", line_range="L1-L2",
                description="Fix it", code_before="x=1", code_after="x=2"
            ),
        ],
        meta={"model": "deepseek-chat", "mock": True},
    )


@pytest.fixture
def runner():
    """Click CLI 测试运行器。"""
    return CliRunner()


@patch("src.main.review_pr_diff")
class TestCLIReviewMode:
    """--review 模式测试"""

    def test_review_flag_produces_output(self, mock_review, runner):
        mock_review.return_value = _make_mock_result()
        result = runner.invoke(cli, [
            "--owner", "test", "--repo", "test", "--pr", "1", "--review"
        ])
        assert result.exit_code == 0
        assert "Test summary" in result.output

    def test_review_json_format(self, mock_review, runner):
        mock_review.return_value = _make_mock_result()
        result = runner.invoke(cli, [
            "--owner", "test", "--repo", "test", "--pr", "1",
            "--review", "--format", "json",
        ])
        assert result.exit_code == 0
        # 输出包含 config 状态 + JSON；提取 JSON 部分验证
        assert '"summary":' in result.output
        assert '"risk_items":' in result.output
        assert '"Test summary."' in result.output

    def test_review_has_risk_level_in_stderr(self, mock_review, runner):
        mock_review.return_value = _make_mock_result()
        result = runner.invoke(cli, [
            "--owner", "test", "--repo", "test", "--pr", "1", "--review"
        ])
        assert "HIGH" in result.stderr


@patch("src.main.capture_pr_diff")
class TestCLIDiffModeStillWorks:
    """向后兼容：无 --review flag 时行为不变"""

    def test_diff_summary_still_works(self, mock_capture, runner):
        """模拟有 structured_diff 的结果"""
        from src.github.pr_capture import PrCaptureWithDiff
        from src.github.types import PrInfo, StructuredDiff, StructuredDiffFile

        mock_result = PrCaptureWithDiff(
            pr=PrInfo(
                number=1, title="Test", body=None, state="open",
                draft=False, head_ref="feat", base_ref="main",
                author="test", created_at="", updated_at="",
                html_url="https://github.com/test/test/pull/1",
            ),
            files_changed=1, additions=5, deletions=2,
            structured_diff=StructuredDiff(
                files=[
                    StructuredDiffFile(
                        filename="a.py", status="added",
                        additions=5, deletions=0, hunks=[]
                    )
                ],
                files_changed=1, additions=5, deletions=2,
            ),
        )
        mock_capture.return_value = mock_result

        result = runner.invoke(cli, [
            "--owner", "test", "--repo", "test", "--pr", "1",
            "--format", "summary",
        ])
        assert result.exit_code == 0
        assert "PR Diff Summary" in result.output

    def test_diff_json_still_works(self, mock_capture, runner):
        from src.github.pr_capture import PrCaptureWithDiff
        from src.github.types import PrInfo, StructuredDiff

        mock_result = PrCaptureWithDiff(
            pr=PrInfo(
                number=1, title="Test", body=None, state="open",
                draft=False, head_ref="feat", base_ref="main",
                author="test", created_at="", updated_at="",
                html_url="https://github.com/test/test/pull/1",
            ),
            files_changed=0, additions=0, deletions=0,
            structured_diff=StructuredDiff(),
        )
        mock_capture.return_value = mock_result

        result = runner.invoke(cli, [
            "--owner", "test", "--repo", "test", "--pr", "1",
            "--format", "json",
        ])
        assert result.exit_code == 0
        # 输出包含 config 状态 + JSON
        assert '"pr":' in result.output
        assert '"structured_diff":' in result.output
