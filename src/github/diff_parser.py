"""
Unified Diff 文本 → 结构化数据 解析器。

支持的格式：unified diff（标准 git diff -U3 输出）
解析层级：文件级 → Hunk 级 → 行级
"""

import re
from typing import Optional
from src.github.types import (
    DiffLine,
    DiffHunk,
    StructuredDiffFile,
    StructuredDiff,
    PrFile,
)

# 文件头正则：diff --git a/<path> b/<path>
_FILE_HEADER_RE = re.compile(r"^diff --git a/(.*?) b/(.*?)$")

# 非代码元信息行
_INDEX_RE = re.compile(
    r"^(index|new file mode|deleted file mode|old mode|new mode|"
    r"similarity index|rename from|rename to|copy from|copy to|Binary files)"
)

# Hunk 头正则：@@ -oldStart[,oldLines] +newStart[,newLines] @@ [context]
_HUNK_HEADER_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)?$")


def _parse_hunk_header(line: str) -> Optional[DiffHunk]:
    """解析 hunk 头行，提取行号范围。"""
    m = _HUNK_HEADER_RE.match(line)
    if not m:
        return None
    return DiffHunk(
        header=line,
        old_start=int(m.group(1)),
        old_lines=int(m.group(2)) if m.group(2) is not None else 1,
        new_start=int(m.group(3)),
        new_lines=int(m.group(4)) if m.group(4) is not None else 1,
    )


def _parse_line(line: str) -> tuple[str, str]:
    """解析单行的类型与内容（去掉前缀 + - 空格）。"""
    if line.startswith("+"):
        return "addition", line[1:]
    if line.startswith("-"):
        return "deletion", line[1:]
    content = line[1:] if line.startswith(" ") else line
    return "context", content


def parse_patch(patch: str) -> list[DiffHunk]:
    """解析单个文件的全量 unified diff patch 文本，返回 Hunk 列表。"""
    # rstrip 去掉末尾换行产生的空行
    lines = patch.rstrip("\n").split("\n")
    hunks: list[DiffHunk] = []
    current: Optional[DiffHunk] = None
    old_ln = 0
    new_ln = 0

    for line in lines:
        # 跳过文件头行
        if (
            _FILE_HEADER_RE.match(line)
            or line.startswith("--- ")
            or line.startswith("+++ ")
            or _INDEX_RE.match(line)
        ):
            continue

        # Hunk 头行
        if line.startswith("@@"):
            if current:
                hunks.append(current)
            hunk = _parse_hunk_header(line)
            if hunk:
                current = hunk
                old_ln = hunk.old_start
                new_ln = hunk.new_start
            continue

        if current is None:
            continue

        # 空行视为 context
        if line == "":
            current.lines.append(DiffLine(
                type="context", old_line=old_ln, new_line=new_ln, content=""
            ))
            old_ln += 1
            new_ln += 1
            continue

        # 普通行
        typ, content = _parse_line(line)
        dl = DiffLine(type=typ, content=content)

        if typ == "context":
            dl.old_line = old_ln
            dl.new_line = new_ln
            old_ln += 1
            new_ln += 1
        elif typ == "deletion":
            dl.old_line = old_ln
            old_ln += 1
        elif typ == "addition":
            dl.new_line = new_ln
            new_ln += 1

        current.lines.append(dl)

    if current:
        hunks.append(current)

    return hunks


def _resolve_status(file: PrFile, patch: str) -> str:
    """综合 API status 和 patch 头判断最终状态。"""
    if file.status == "added":
        return "added"
    if file.status == "removed":
        return "removed"
    if file.status == "renamed":
        return "renamed"

    head = patch[:200]
    if "new file mode" in head:
        return "added"
    if "deleted file mode" in head:
        return "removed"
    if "rename from" in head or "rename to" in head:
        return "renamed"

    return "modified"


def parse_file_diff(file: PrFile) -> StructuredDiffFile:
    """解析单个文件（PrFile + patch），返回结构化 Diff。"""
    patch = file.patch or ""
    status = _resolve_status(file, patch)
    hunks = parse_patch(patch)

    additions = (
        sum(sum(1 for l in h.lines if l.type == "addition") for h in hunks)
        if hunks else file.additions
    )
    deletions = (
        sum(sum(1 for l in h.lines if l.type == "deletion") for h in hunks)
        if hunks else file.deletions
    )

    return StructuredDiffFile(
        filename=file.filename,
        status=status,
        additions=additions,
        deletions=deletions,
        previous_filename=file.previous_filename,
        hunks=hunks,
    )


def parse_diff(files: list[PrFile]) -> StructuredDiff:
    """将 PrFile 列表解析为完整的 StructuredDiff。"""
    parsed = [parse_file_diff(f) for f in files]
    return StructuredDiff(
        files=parsed,
        files_changed=len(files),
        additions=sum(f.additions for f in parsed),
        deletions=sum(f.deletions for f in parsed),
    )


def summarize_diff(diff: StructuredDiff) -> str:
    """从结构化 Diff 生成 Markdown 摘要（适合 AI Review 输入）。"""
    parts = [
        "# PR Diff Summary",
        f"Files: {diff.files_changed} changed, +{diff.additions} -{diff.deletions}",
        "",
    ]

    ICON = {"added": "[+]", "removed": "[-]", "renamed": "[~]", "modified": "[*]"}

    for f in diff.files:
        icon = ICON.get(f.status, "📄")
        parts.append(f"### {icon} {f.filename} ({f.status}, +{f.additions}/-{f.deletions})")

        for h in f.hunks:
            parts.append(f"  {h.header}")
            for line in h.lines[:5]:
                pfx = {"addition": "+", "deletion": "-"}.get(line.type, " ")
                parts.append(f"    {pfx} {line.content}")
            if len(h.lines) > 5:
                parts.append(f"    ... ({len(h.lines) - 5} more lines)")
        parts.append("")

    return "\n".join(parts)


# ====================================================================
# 开发调试入口
# ====================================================================
if __name__ == "__main__":
    sample = """diff --git a/src/config.py b/src/config.py
new file mode 100644
index 0000000..a1b2c3d
--- /dev/null
+++ b/src/config.py
@@ -0,0 +1,6 @@
+from dataclasses import dataclass
+from pathlib import Path
+
+def get_config():
+    token = None
+    return {"token": token}"""

    f = PrFile(filename="src/config.py", status="added", additions=6, deletions=0, changes=6, patch=sample)
    result = parse_file_diff(f)
    from dataclasses import asdict
    import json
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
