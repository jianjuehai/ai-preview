"""
GitHub API 客户端 —— 基于 PyGithub 进行认证与请求。
无 Token 或 API 失败时自动降级到本地 Mock 数据。
"""

import json
from pathlib import Path
from typing import Optional

from github import Github, GithubException, Auth
from github.PullRequest import PullRequest
from github.File import File
from github.GitCommit import GitCommit

from src.config import get_config
from src.github.types import PrInfo, PrFile, PrCommit, PrCaptureResult


# Mock 数据文件路径
_MOCK_PATH = Path(__file__).resolve().parent.parent.parent / "tests" / "mock_data" / "sample_pr.json"

# 缓存已加载的 mock 数据
_mock_cache: Optional[dict] = None


def _load_mock() -> dict:
    """加载 Mock 数据（带缓存）。"""
    global _mock_cache
    if _mock_cache is None:
        _mock_cache = json.loads(_MOCK_PATH.read_text(encoding="utf-8"))
    return _mock_cache


def _map_pr(pr: PullRequest) -> PrInfo:
    """将 PyGithub PullRequest 映射为 PrInfo。"""
    return PrInfo(
        number=pr.number,
        title=pr.title,
        body=pr.body,
        state=pr.state if pr.state in ("open", "closed") else "merged",
        draft=pr.draft,
        head_ref=pr.head.ref,
        base_ref=pr.base.ref,
        author=pr.user.login if pr.user else "unknown",
        created_at=pr.created_at.isoformat() if pr.created_at else "",
        updated_at=pr.updated_at.isoformat() if pr.updated_at else "",
        html_url=pr.html_url,
    )


def _map_file(f: File) -> PrFile:
    """将 PyGithub File 映射为 PrFile。"""
    return PrFile(
        filename=f.filename,
        status=f.status,
        additions=f.additions,
        deletions=f.deletions,
        changes=f.changes,
        patch=f.patch,
        previous_filename=f.previous_filename,
    )


def _map_commit(c: GitCommit) -> PrCommit:
    """将 PyGithub GitCommit 映射为 PrCommit。"""
    return PrCommit(
        sha=c.sha,
        message=c.commit.message if c.commit else "",
        author=c.commit.author.name if c.commit and c.commit.author else "unknown",
        date=c.commit.author.date.isoformat() if c.commit and c.commit.author and c.commit.author.date else "",
    )


def _get_github() -> Optional[Github]:
    """获取 PyGithub 客户端实例。Token 不可用时返回 None。"""
    config = get_config()
    if not config.github_token:
        return None
    return Github(auth=Auth.Token(config.github_token))


# ====================================================================
# 公开 API
# ====================================================================

def get_pr_detail(owner: str, repo: str, pr_number: int) -> PrInfo:
    """获取指定 PR 的元数据。API 失败时自动返回 Mock 数据。"""
    g = _get_github()
    if g is None:
        print("[github/client] No GitHub token — using mock data")
        return PrInfo(**_load_mock()["pr"])

    try:
        gh_repo = g.get_repo(f"{owner}/{repo}")
        pr = gh_repo.get_pull(pr_number)
        return _map_pr(pr)
    except GithubException as e:
        print(f"[github/client] API error (HTTP {e.status}) — falling back to mock data")
        return PrInfo(**_load_mock()["pr"])


def get_pr_files(owner: str, repo: str, pr_number: int) -> list[PrFile]:
    """获取指定 PR 的变更文件列表（含 diff patch）。API 失败时自动返回 Mock 数据。"""
    g = _get_github()
    if g is None:
        print("[github/client] No GitHub token — using mock data")
        return [PrFile(**f) for f in _load_mock()["files"]]

    try:
        gh_repo = g.get_repo(f"{owner}/{repo}")
        pr = gh_repo.get_pull(pr_number)
        return [_map_file(f) for f in pr.get_files()]
    except GithubException as e:
        print(f"[github/client] API error (HTTP {e.status}) — falling back to mock data")
        return [PrFile(**f) for f in _load_mock()["files"]]


def list_pr_commits(owner: str, repo: str, pr_number: int) -> list[PrCommit]:
    """获取指定 PR 关联的 Commit 列表。API 失败时自动返回 Mock 数据。"""
    g = _get_github()
    if g is None:
        print("[github/client] No GitHub token — using mock data")
        return [PrCommit(**c) for c in _load_mock()["commits"]]

    try:
        gh_repo = g.get_repo(f"{owner}/{repo}")
        pr = gh_repo.get_pull(pr_number)
        return [_map_commit(c) for c in pr.get_commits()]
    except GithubException as e:
        print(f"[github/client] API error (HTTP {e.status}) — falling back to mock data")
        return [PrCommit(**c) for c in _load_mock()["commits"]]


def capture_pr_data(owner: str, repo: str, pr_number: int) -> PrCaptureResult:
    """一站式获取 PR 完整数据（pr + files + commits + 统计）。"""
    pr = get_pr_detail(owner, repo, pr_number)
    files = get_pr_files(owner, repo, pr_number)
    commits = list_pr_commits(owner, repo, pr_number)

    return PrCaptureResult(
        pr=pr,
        files=files,
        commits=commits,
        files_changed=len(files),
        additions=sum(f.additions for f in files),
        deletions=sum(f.deletions for f in files),
    )


# ====================================================================
# 开发调试入口
# ====================================================================
if __name__ == "__main__":
    import sys

    owner = sys.argv[1] if len(sys.argv) > 1 else "jianjuehai"
    repo = sys.argv[2] if len(sys.argv) > 2 else "AI-PR-Review"
    pr_num = int(sys.argv[3]) if len(sys.argv) > 3 else 1

    result = capture_pr_data(owner, repo, pr_num)
    print(json.dumps({
        "pr": result.pr.__dict__,
        "files_count": len(result.files),
        "commits_count": len(result.commits),
        "stats": result.stats,
    }, indent=2, ensure_ascii=False))
