"""
GitHub API 客户端 —— 单元测试（基于 Mock 降级模式）。
不依赖真实 API Token，验证 Mock 数据的结构与完整性。
"""

import pytest
from src.github.client import (
    get_pr_detail,
    get_pr_files,
    list_pr_commits,
    capture_pr_data,
)


class TestGetPrDetail:
    """get_pr_detail — Mock 降级测试"""

    def test_returns_valid_pr_info(self):
        pr = get_pr_detail("test-owner", "test-repo", 1)
        assert pr is not None
        assert isinstance(pr.number, int)
        assert isinstance(pr.title, str)
        assert len(pr.title) > 0

    def test_has_all_required_fields(self):
        pr = get_pr_detail("test-owner", "test-repo", 1)
        assert hasattr(pr, "number")
        assert hasattr(pr, "title")
        assert hasattr(pr, "state")
        assert hasattr(pr, "head_ref")
        assert hasattr(pr, "base_ref")
        assert hasattr(pr, "author")
        assert hasattr(pr, "created_at")
        assert hasattr(pr, "html_url")

    def test_state_is_valid(self):
        pr = get_pr_detail("test-owner", "test-repo", 1)
        assert pr.state in ("open", "closed", "merged")

    def test_html_url_is_github_format(self):
        pr = get_pr_detail("test-owner", "test-repo", 1)
        assert pr.html_url.startswith("https://github.com/")


class TestGetPrFiles:
    """get_pr_files — Mock 降级测试"""

    def test_returns_non_empty_file_list(self):
        files = get_pr_files("test-owner", "test-repo", 1)
        assert len(files) > 0

    def test_each_file_has_required_fields(self):
        files = get_pr_files("test-owner", "test-repo", 1)
        for f in files:
            assert hasattr(f, "filename")
            assert hasattr(f, "status")
            assert isinstance(f.filename, str)
            assert len(f.filename) > 0

    def test_status_is_valid(self):
        files = get_pr_files("test-owner", "test-repo", 1)
        valid = {"added", "modified", "removed", "renamed", "copied", "changed"}
        for f in files:
            assert f.status in valid

    def test_added_files_have_additions(self):
        files = get_pr_files("test-owner", "test-repo", 1)
        for f in files:
            if f.status == "added":
                assert f.additions > 0
                assert f.deletions == 0

    def test_removed_files_have_deletions(self):
        files = get_pr_files("test-owner", "test-repo", 1)
        for f in files:
            if f.status == "removed":
                assert f.deletions > 0
                assert f.additions == 0

    def test_at_least_one_file_has_patch(self):
        files = get_pr_files("test-owner", "test-repo", 1)
        files_with_patch = [f for f in files if f.patch and len(f.patch) > 0]
        assert len(files_with_patch) > 0


class TestListPrCommits:
    """list_pr_commits — Mock 降级测试"""

    def test_returns_non_empty_commit_list(self):
        commits = list_pr_commits("test-owner", "test-repo", 1)
        assert len(commits) > 0

    def test_each_commit_has_required_fields(self):
        commits = list_pr_commits("test-owner", "test-repo", 1)
        for c in commits:
            assert hasattr(c, "sha")
            assert hasattr(c, "message")
            assert hasattr(c, "author")
            assert hasattr(c, "date")

    def test_sha_is_40_char_hex(self):
        commits = list_pr_commits("test-owner", "test-repo", 1)
        for c in commits:
            assert len(c.sha) == 40
            assert all(ch in "abcdef0123456789" for ch in c.sha.lower())


class TestCapturePrData:
    """capture_pr_data — 一站式捕获测试"""

    def test_returns_complete_result_with_correct_stats(self):
        result = capture_pr_data("test-owner", "test-repo", 1)

        assert result.pr is not None
        assert len(result.files) > 0
        assert len(result.commits) > 0

        # stats 应与 files 数据一致
        assert result.files_changed == len(result.files)
        assert result.additions == sum(f.additions for f in result.files)
        assert result.deletions == sum(f.deletions for f in result.files)

    def test_stats_property(self):
        result = capture_pr_data("test-owner", "test-repo", 1)
        s = result.stats
        assert s["files_changed"] == result.files_changed
        assert s["additions"] == result.additions
        assert s["deletions"] == result.deletions
