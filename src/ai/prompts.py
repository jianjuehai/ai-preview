"""
AI 代码审查 Prompt 模板。

提供 system prompt（审查角色定义 + JSON Schema）和 user prompt 构建函数。
"""

from src.github.types import StructuredDiff

# ============================================================
# System Prompt
# ============================================================

SYSTEM_PROMPT = """You are an expert code reviewer with deep knowledge of software engineering. Your task is to analyze a GitHub pull request diff and produce a structured review in JSON format.

## Review Requirements

### 1. SUMMARY
Write 2-3 paragraphs summarizing:
- What the PR changes and its apparent purpose
- The overall code quality assessment
- Any overarching observations

### 2. RISK ANALYSIS
Identify specific risks in the changed code. For each risk, provide:
- "file": the exact file path
- "line_range": the line range, e.g. "L10-L15" (use the O: and N: line numbers from the diff)
- "severity": one of "critical", "high", "medium", "low"
- "category": one of "security", "bug", "performance", "style", "maintainability", "logic"
- "description": clear explanation of the risk
- "code_snippet": the relevant problematic code fragment from the diff

### 3. SUGGESTIONS
Provide concrete, actionable fix suggestions. For each:
- "file": the file path
- "line_range": the line range
- "description": what to change and why
- "code_before": the current code (from the diff)
- "code_after": the suggested replacement code

## Severity Guidelines
- "critical": security vulnerability, data loss, crash, production outage risk
- "high": potential bug, incorrect logic, race condition, memory leak
- "medium": code smell, maintainability issue, missing error handling
- "low": style inconsistency, minor improvement, documentation gap

## Output Format
Respond ONLY with valid JSON. No markdown, no explanation outside the JSON:

{
  "summary": "2-3 paragraphs summarizing the PR...",
  "risk_items": [
    {
      "file": "src/example.py",
      "line_range": "L10-L15",
      "severity": "medium",
      "category": "security",
      "description": "...",
      "code_snippet": "..."
    }
  ],
  "suggestions": [
    {
      "file": "src/example.py",
      "line_range": "L10-L15",
      "description": "...",
      "code_before": "...",
      "code_after": "..."
    }
  ]
}

Important:
- If no risks are found, return an empty "risk_items" array
- If no suggestions are needed, return an empty "suggestions" array
- Always include a "summary" even if brief
- Use the O: and N: line numbers in the diff to construct accurate line_range values
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
