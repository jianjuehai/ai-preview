"""
GitHub API 相关类型定义 —— 使用 dataclass 提供类型安全的数据结构。
"""

from dataclasses import dataclass, field
from typing import Optional, Literal


@dataclass
class PrInfo:
    """PR 元数据。"""
    number: int
    title: str
    body: Optional[str]
    state: Literal["open", "closed", "merged"]
    draft: bool
    head_ref: str          # 源分支名
    base_ref: str          # 目标分支名
    author: str            # GitHub 用户名
    created_at: str        # ISO 8601
    updated_at: str        # ISO 8601
    html_url: str          # PR 网页链接


@dataclass
class PrFile:
    """单个变更文件的信息。"""
    filename: str
    status: Literal["added", "modified", "removed", "renamed", "copied", "changed"]
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None               # unified diff patch（可能为空）
    previous_filename: Optional[str] = None   # 原文件路径（仅 renamed 时有值）


@dataclass
class PrCommit:
    """PR 关联的 Commit 摘要。"""
    sha: str
    message: str
    author: str
    date: str


@dataclass
class PrCaptureResult:
    """PR 数据捕获的完整输出（供下游 AI Review 消费）。"""
    pr: PrInfo
    files: list[PrFile] = field(default_factory=list)
    commits: list[PrCommit] = field(default_factory=list)
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0

    @property
    def stats(self) -> dict:
        return {
            "files_changed": self.files_changed,
            "additions": self.additions,
            "deletions": self.deletions,
        }


# ============================================================
# Diff 结构化解析相关类型
# ============================================================

@dataclass
class DiffLine:
    """Diff 中的一行。"""
    type: Literal["context", "addition", "deletion"]
    content: str
    old_line: Optional[int] = None   # 旧文件行号（deletion/context）
    new_line: Optional[int] = None   # 新文件行号（addition/context）


@dataclass
class DiffHunk:
    """Diff 中的一个 Hunk（变更块）。"""
    header: str             # @@ -1,5 +1,7 @@
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    lines: list[DiffLine] = field(default_factory=list)


@dataclass
class StructuredDiffFile:
    """单个文件的结构化 Diff。"""
    filename: str
    status: Literal["added", "modified", "removed", "renamed"]
    additions: int
    deletions: int
    previous_filename: Optional[str] = None
    hunks: list[DiffHunk] = field(default_factory=list)


@dataclass
class StructuredDiff:
    """完整 PR 的结构化 Diff 输出（供下游 AI Review 消费）。"""
    files: list[StructuredDiffFile] = field(default_factory=list)
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0

    @property
    def stats(self) -> dict:
        return {
            "files_changed": self.files_changed,
            "additions": self.additions,
            "deletions": self.deletions,
        }
