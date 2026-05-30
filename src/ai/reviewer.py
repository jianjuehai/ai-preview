"""
AI PR 审查编排器 —— 组合 PR 数据捕获 + Prompt 构建 + DeepSeek API 调用。
"""

from src.ai.client import chat_completion
from src.ai.prompts import build_messages
from src.ai.types import ReviewResult, RiskItem, Suggestion
from src.github.pr_capture import capture_pr_diff


def review_pr_diff(
    owner: str,
    repo: str,
    pr_number: int,
    *,
    model: str = "deepseek-chat",
    temperature: float = 0.3,
) -> ReviewResult:
    """
    对指定 PR 进行完整 AI 代码审查。

    流程:
    1. 捕获 PR Diff 数据（自动 Mock 降级）
    2. 构建 System + User Prompt
    3. 调用 DeepSeek API（自动 Mock 降级）
    4. 解析 AI 响应为 ReviewResult

    参数:
        owner:     仓库所有者
        repo:      仓库名
        pr_number: PR 编号
        model:     模型 ID（默认 deepseek-chat）
        temperature: 生成温度（0.0-1.0，越低越确定）

    返回:
        ReviewResult: 含摘要、风险列表和修复建议的类型化审查结果
    """
    # 1. 捕获 PR 数据
    print(f"[reviewer] Capturing PR data: {owner}/{repo}#{pr_number}")
    captured = capture_pr_diff(owner, repo, pr_number)

    # 2. 构建 Prompt
    messages = build_messages(
        captured.structured_diff,
        pr_title=captured.pr.title,
        pr_body=captured.pr.body or "",
    )

    # 3. 调用 AI
    print(f"[reviewer] Calling DeepSeek API (model={model})")
    raw = chat_completion(
        messages,
        model=model,
        temperature=temperature,
    )

    # 4. 解析结果
    return _parse_response(raw, model)


def _parse_response(raw: dict, model: str = "unknown") -> ReviewResult:
    """
    将 AI 响应的原始 dict 解析为类型安全的 ReviewResult。

    防御性解析：每个字段都有默认值，AI JSON 不完整不会崩溃。
    """
    meta = raw.get("meta", {})
    if not meta:
        meta = {"model": model}

    def _parse_risk(item: dict) -> RiskItem:
        severity = item.get("severity", "low")
        if severity not in ("critical", "high", "medium", "low"):
            severity = "low"
        return RiskItem(
            file=item.get("file", ""),
            line_range=item.get("line_range", ""),
            severity=severity,  # type: ignore
            category=item.get("category", "unknown"),
            description=item.get("description", ""),
            code_snippet=item.get("code_snippet", ""),
        )

    def _parse_suggestion(item: dict) -> Suggestion:
        return Suggestion(
            file=item.get("file", ""),
            line_range=item.get("line_range", ""),
            description=item.get("description", ""),
            code_before=item.get("code_before"),
            code_after=item.get("code_after"),
        )

    return ReviewResult(
        summary=raw.get("summary", "No summary available."),
        risk_items=[_parse_risk(r) for r in raw.get("risk_items", [])],
        suggestions=[_parse_suggestion(s) for s in raw.get("suggestions", [])],
        meta=meta,
    )


# ============================================================
# 开发调试入口
# ============================================================
if __name__ == "__main__":
    import json
    from dataclasses import asdict

    result = review_pr_diff("jianjuehai", "ai-preview", 1)
    print("\n=== Review Result ===")
    print(f"Summary: {result.summary[:200]}...")
    print(f"Risks: {len(result.risk_items)}")
    for r in result.risk_items:
        print(f"  [{r.severity.upper()}] {r.file}:{r.line_range} — {r.category}")
    print(f"Suggestions: {len(result.suggestions)}")
    print(f"Risk Level: {result.overall_risk_level}")
    print(f"Meta: {json.dumps(result.meta)}")
