"""
AI 代码审查 Prompt 模板。

提供 system prompt（审查角色定义 + JSON Schema）和 user prompt 构建函数。
"""

from src.github.types import StructuredDiff

# ============================================================
# System Prompt
# ============================================================

SYSTEM_PROMPT = """你是一位资深的代码审查专家，拥有丰富的软件工程经验。你的任务是分析 GitHub Pull Request 的 diff，并以 JSON 格式输出结构化的中文审查报告。

## 审查要求

### 1. SUMMARY（摘要）
用 2-3 段中文总结：
- 该 PR 改了什么，其目的和意图是什么
- 整体代码质量评估
- 任何全局性的观察和意见

### 2. RISK ANALYSIS（风险分析）
识别变更代码中的具体风险。对每个风险，提供以下字段：
- "file": 文件路径
- "line_range": 行号范围，如 "L10-L15"（利用 diff 中的 O: 和 N: 行号定位）
- "severity": 严重程度，取 "critical"（致命）、"high"（高危）、"medium"（中危）、"low"（低危）之一
- "category": 分类，取 "security"（安全）、"bug"（缺陷）、"performance"（性能）、"style"（风格）、"maintainability"（可维护性）、"logic"（逻辑）之一
- "description": 用中文清晰描述该风险
- "code_snippet": 问题代码片段（从 diff 中提取）

### 3. SUGGESTIONS（修复建议）
提供具体、可操作的修复建议。对每条建议：
- "file": 文件路径
- "line_range": 行号范围
- "description": 用中文描述修改方案和原因
- "code_before": 当前代码（从 diff 中提取）
- "code_after": 建议修改后的代码

## 严重程度指南
- "critical"（致命）：安全漏洞、数据丢失、服务崩溃、生产事故风险
- "high"（高危）：潜在 bug、逻辑错误、竞态条件、内存泄漏
- "medium"（中危）：代码异味、可维护性问题、缺少错误处理
- "low"（低危）：风格不一致、命名不规范、文档缺失

## 输出格式
请**只返回**合法的 JSON，不要包含 markdown 标记或 JSON 之外的任何解释文字：

{
  "summary": "用 2-3 段中文总结该 PR 的变更内容…",
  "risk_items": [
    {
      "file": "src/example.py",
      "line_range": "L10-L15",
      "severity": "medium",
      "category": "security",
      "description": "用中文描述该风险…",
      "code_snippet": "相关代码片段…"
    }
  ],
  "suggestions": [
    {
      "file": "src/example.py",
      "line_range": "L10-L15",
      "description": "用中文描述修改建议…",
      "code_before": "修改前的代码…",
      "code_after": "修改后的代码…"
    }
  ]
}

重要提示：
- 如果没有发现风险，risk_items 设为空数组 []
- 如果没有修复建议，suggestions 设为空数组 []
- summary 字段即使简短也必须提供
- 所有 description 字段请用中文撰写
- 代码片段（code_snippet、code_before、code_after）保持原文不变
"""

# ============================================================
# User Prompt Builder
# ============================================================

def build_user_prompt(
    diff: StructuredDiff,
    pr_title: str = "",
    pr_body: str = "",
) -> str:
    """
    从结构化 Diff 构建 user prompt。

    包含:
    - PR 标题和描述（作为上下文）
    - Diff 统计摘要
    - 逐文件、逐 Hunk、逐行的完整 diff（含精确行号）
    """
    parts: list[str] = []

    # --- PR 上下文 ---
    if pr_title:
        parts.append(f"## PR Title\n{pr_title}\n")
    if pr_body:
        parts.append(f"## PR Description\n{pr_body}\n")

    # --- 统计摘要 ---
    parts.append(
        f"## Diff Stats\n"
        f"Files changed: {diff.files_changed}, "
        f"Additions: +{diff.additions}, "
        f"Deletions: -{diff.deletions}\n"
    )

    # --- 逐文件 Diff ---
    parts.append("## Changed Files\n")
    for f in diff.files:
        icon = {"added": "+", "removed": "-", "renamed": "~", "modified": "*"}.get(f.status, "*")
        parts.append(
            f"\n### [{icon}] {f.filename} "
            f"(status={f.status}, +{f.additions}/-{f.deletions})"
        )
        if f.previous_filename:
            parts.append(f"    (renamed from: {f.previous_filename})")

        for hunk in f.hunks:
            parts.append(f"  {hunk.header}")
            for line in hunk.lines:
                prefix = {"addition": "+", "deletion": "-"}.get(line.type, " ")
                # 构造行号信息
                ln_info_parts = []
                if line.old_line is not None:
                    ln_info_parts.append(f"O:{line.old_line}")
                if line.new_line is not None:
                    ln_info_parts.append(f"N:{line.new_line}")
                ln_info = ",".join(ln_info_parts)
                parts.append(f"    {prefix} [{ln_info}] {line.content}")

    return "\n".join(parts)


def build_messages(
    diff: StructuredDiff,
    pr_title: str = "",
    pr_body: str = "",
) -> list[dict]:
    """
    构建完整的对话消息列表，可直接传入 chat_completion()。
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(diff, pr_title, pr_body)},
    ]


# ============================================================
# 开发调试入口
# ============================================================
if __name__ == "__main__":
    from src.github.pr_capture import capture_pr_diff
    from src.github.diff_parser import summarize_diff

    result = capture_pr_diff("test", "test", 1)
    messages = build_messages(
        result.structured_diff,
        pr_title=result.pr.title,
        pr_body=result.pr.body or "",
    )
    print(f"System prompt length: {len(messages[0]['content'])} chars")
    print(f"User prompt length:   {len(messages[1]['content'])} chars")
    print("\n--- SYSTEM PROMPT (first 200 chars) ---")
    print(messages[0]["content"][:200])
    print("\n--- USER PROMPT (first 300 chars) ---")
    print(messages[1]["content"][:300])
