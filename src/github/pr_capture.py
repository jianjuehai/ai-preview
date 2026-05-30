"""
PR 数据捕获模块 —— 组合 GitHub API 客户端与 Diff 解析器。
"""

from dataclasses import dataclass, field, asdict
from typing import Optional

from src.github.client import capture_pr_data
from src.github.diff_parser import parse_diff, summarize_diff
from src.github.types import (
    PrInfo,
    PrFile,
    PrCommit,
    StructuredDiff,
)


@dataclass
class PrCaptureWithDiff:
    """PR 完整捕获结果（含结构化 Diff）。"""
    pr: PrInfo
    files: list[PrFile] = field(default_factory=list)
    commits: list[PrCommit] = field(default_factory=list)
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    structured_diff: Optional[StructuredDiff] = None

    @property
    def stats(self) -> dict:
        return {
            "files_changed": self.files_changed,
            "additions": self.additions,
            "deletions": self.deletions,
        }

    def to_dict(self) -> dict:
        """转为可 JSON 序列化的字典。"""
        d = asdict(self)
        d["structured_diff"] = {
            "files": [
                {
                    "filename": f.filename,
                    "status": f.status,
                    "additions": f.additions,
                    "deletions": f.deletions,
                    "previous_filename": f.previous_filename,
                    "hunks": [
                        {
                            "header": h.header,
                            "old_start": h.old_start,
                            "new_start": h.new_start,
                            "lines": [
                                {k: v for k, v in l.items() if v is not None}
                                for l in [asdict(line) for line in h.lines]
                            ],
                        }
                        for h in f.hunks
                    ],
                }
                for f in self.structured_diff.files
            ],
            "stats": self.structured_diff.stats,
        }
        return d


def capture_pr_diff(owner: str, repo: str, pr_number: int) -> PrCaptureWithDiff:
    """一站式 PR 数据捕获（含结构化 Diff）。"""
    raw = capture_pr_data(owner, repo, pr_number)
    structured = parse_diff(raw.files)

    return PrCaptureWithDiff(
        pr=raw.pr,
        files=raw.files,
        commits=raw.commits,
        files_changed=raw.files_changed,
        additions=raw.additions,
        deletions=raw.deletions,
        structured_diff=structured,
    )


# ====================================================================
# 开发调试入口
# ====================================================================
if __name__ == "__main__":
    import json

    result = capture_pr_diff("jianjuehai", "AI-PR-Review", 1)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    print()
    print(summarize_diff(result.structured_diff))
