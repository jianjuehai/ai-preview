#!/usr/bin/env python3
"""
Diff 解析器 —— 单元测试。
覆盖：新增文件、删除文件、修改文件、多 hunk、空 patch、行号追踪。
"""

import pytest
from src.github.diff_parser import (
    parse_patch,
    parse_file_diff,
    parse_diff,
    summarize_diff,
)
from src.github.types import (
    PrFile,
    DiffLine,
    DiffHunk,
    StructuredDiffFile,
    StructuredDiff,
)


def _make_file(**kw) -> PrFile:
    defaults = dict(
        filename="src/test.py",
        status="modified",
        additions=0,
        deletions=0,
        changes=0,
        patch="",
    )
    defaults.update(kw)
    return PrFile(**defaults)


# ============================================================
# parse_patch
# ============================================================

class TestParsePatch:
    def test_added_file_single_hunk(self):
        patch = (
            "diff --git a/src/new.py b/src/new.py\n"
            "new file mode 100644\n"
            "index 0000000..a1b2c3d\n"
            "--- /dev/null\n"
            "+++ b/src/new.py\n"
            "@@ -0,0 +1,3 @@\n"
            "+import os\n"
            "+\n"
            "+print('hello')\n"
        )
        hunks = parse_patch(patch)
        assert len(hunks) == 1
        h = hunks[0]
        assert h.old_start == 0
        assert h.new_start == 1
        assert h.new_lines == 3
        assert len(h.lines) == 3
        assert all(l.type == "addition" for l in h.lines)
        assert h.lines[0].content == "import os"
        assert h.lines[1].content == ""   # 空行

    def test_deleted_file_single_hunk(self):
        patch = (
            "diff --git a/src/old.py b/src/old.py\n"
            "deleted file mode 100644\n"
            "index abc1234..0000000\n"
            "--- a/src/old.py\n"
            "+++ /dev/null\n"
            "@@ -1,3 +0,0 @@\n"
            "-x = 1\n"
            "-y = 2\n"
            "-print(x + y)\n"
        )
        hunks = parse_patch(patch)
        assert len(hunks) == 1
        assert hunks[0].old_start == 1
        assert hunks[0].new_start == 0
        assert all(l.type == "deletion" for l in hunks[0].lines)

    def test_modified_multi_hunk(self):
        patch = (
            "diff --git a/src/calc.py b/src/calc.py\n"
            "index a1b2c3d..e4f5g6h 100644\n"
            "--- a/src/calc.py\n"
            "+++ b/src/calc.py\n"
            "@@ -1,4 +1,4 @@\n"
            " def add(a, b):\n"
            "-    return a + b\n"
            "+    return a - b\n"
            " \n"
            "@@ -10,3 +10,4 @@\n"
            " def mul(a, b):\n"
            "     return a * b\n"
            "+print('done')\n"
        )
        hunks = parse_patch(patch)
        assert len(hunks) == 2
        # Hunk 1
        del_line = next(l for l in hunks[0].lines if l.type == "deletion")
        add_line = next(l for l in hunks[0].lines if l.type == "addition")
        assert del_line.content == "    return a + b"
        assert add_line.content == "    return a - b"
        # Hunk 2
        assert hunks[1].old_start == 10
        assert hunks[1].lines[-1].type == "addition"

    def test_empty_patch(self):
        assert parse_patch("") == []

    def test_no_newline_marker(self):
        patch = (
            "diff --git a/src/eof.py b/src/eof.py\n"
            "--- a/src/eof.py\n"
            "+++ b/src/eof.py\n"
            "@@ -1,2 +1,2 @@\n"
            " x = 1\n"
            "-y = 2\n"
            "+y = 3\n"
            "\\ No newline at end of file\n"
        )
        hunks = parse_patch(patch)
        assert len(hunks) == 1
        last = hunks[0].lines[-1]
        assert "No newline" in last.content

    def test_line_numbers_tracked_correctly(self):
        patch = (
            "diff --git a/src/num.py b/src/num.py\n"
            "--- a/src/num.py\n"
            "+++ b/src/num.py\n"
            "@@ -5,3 +5,3 @@\n"
            " keep\n"
            "-removed\n"
            "+added\n"
            " keep2\n"
        )
        hunks = parse_patch(patch)
        lines = hunks[0].lines

        assert lines[0].type == "context"
        assert lines[0].old_line == 5
        assert lines[0].new_line == 5

        assert lines[1].type == "deletion"
        assert lines[1].old_line == 6
        assert lines[1].new_line is None

        assert lines[2].type == "addition"
        assert lines[2].old_line is None
        assert lines[2].new_line == 6

        assert lines[3].type == "context"
        assert lines[3].old_line == 7
        assert lines[3].new_line == 7


# ============================================================
# parse_file_diff
# ============================================================

class TestParseFileDiff:
    def test_added_file(self):
        f = _make_file(filename="src/new.py", status="added", additions=3,
                       patch="diff --git a/src/new.py b/src/new.py\n"
                             "new file mode 100644\n"
                             "--- /dev/null\n+++ b/src/new.py\n"
                             "@@ -0,0 +1,3 @@\n+1\n+2\n+3\n")
        r = parse_file_diff(f)
        assert r.status == "added"
        assert r.filename == "src/new.py"
        assert r.deletions == 0
        assert len(r.hunks) == 1

    def test_deleted_file(self):
        f = _make_file(filename="src/d.py", status="removed", deletions=3,
                       patch="diff --git a/src/d.py b/src/d.py\n"
                             "deleted file mode 100644\n"
                             "--- a/src/d.py\n+++ /dev/null\n"
                             "@@ -1,3 +0,0 @@\n-1\n-2\n-3\n")
        r = parse_file_diff(f)
        assert r.status == "removed"
        assert r.additions == 0

    def test_modified_file(self):
        f = _make_file(filename="src/m.py", status="modified",
                       patch="diff --git a/src/m.py b/src/m.py\n"
                             "--- a/src/m.py\n+++ b/src/m.py\n"
                             "@@ -1,1 +1,1 @@\n-old\n+new\n")
        r = parse_file_diff(f)
        assert r.status == "modified"

    def test_renamed_file(self):
        f = _make_file(filename="src/new.py", status="renamed",
                       previous_filename="src/old.py",
                       patch="diff --git a/src/old.py b/src/new.py\n"
                             "rename from src/old.py\nrename to src/new.py\n")
        r = parse_file_diff(f)
        assert r.status == "renamed"
        assert r.previous_filename == "src/old.py"

    def test_no_patch_uses_file_level_stats(self):
        f = _make_file(filename="binary.png", status="modified", additions=0, patch=None)
        r = parse_file_diff(f)
        assert r.hunks == []
        assert r.additions == 0
        assert r.deletions == 0


# ============================================================
# parse_diff
# ============================================================

class TestParseDiff:
    def test_multi_file_with_stats(self):
        files = [
            _make_file(filename="a.py", status="added", additions=5,
                       patch="diff --git a/a.py b/a.py\nnew file mode 100644\n"
                             "--- /dev/null\n+++ b/a.py\n"
                             "@@ -0,0 +1,5 @@\n+1\n+2\n+3\n+4\n+5\n"),
            _make_file(filename="b.py", status="removed", deletions=3,
                       patch="diff --git a/b.py b/b.py\ndeleted file mode 100644\n"
                             "--- a/b.py\n+++ /dev/null\n"
                             "@@ -1,3 +0,0 @@\n-1\n-2\n-3\n"),
        ]
        r = parse_diff(files)
        assert len(r.files) == 2
        assert r.files_changed == 2
        assert r.additions == 5
        assert r.deletions == 3

    def test_empty_files(self):
        r = parse_diff([])
        assert r.files == []
        assert r.files_changed == 0


# ============================================================
# summarize_diff
# ============================================================

class TestSummarizeDiff:
    def test_generates_summary_text(self):
        f = StructuredDiffFile(
            filename="src/app.py",
            status="modified",
            additions=2,
            deletions=1,
            hunks=[
                DiffHunk(
                    header="@@ -1,3 +1,4 @@",
                    old_start=1, old_lines=3,
                    new_start=1, new_lines=4,
                    lines=[
                        DiffLine("context", "import x", old_line=1, new_line=1),
                        DiffLine("deletion", "y = 1", old_line=2),
                        DiffLine("addition", "y = 2", new_line=2),
                        DiffLine("context", "export", old_line=3, new_line=3),
                    ],
                )
            ],
        )
        diff = StructuredDiff(files=[f], files_changed=1, additions=2, deletions=1)
        s = summarize_diff(diff)
        assert "PR Diff Summary" in s
        assert "src/app.py" in s
        assert "modified" in s
        assert "+2/-1" in s
        assert "@@ -1,3 +1,4 @@" in s
