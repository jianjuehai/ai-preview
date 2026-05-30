#!/usr/bin/env python3
"""
AI PR Review Assistant — CLI 入口

用法：
    # Diff 捕获模式
    python -m src.main --owner <owner> --repo <repo> --pr <number>
    python -m src.main --owner jianjuehai --repo ai-preview --pr 1 --format summary

    # AI 审查模式
    python -m src.main --owner <owner> --repo <repo> --pr <number> --review
    python -m src.main --owner jianjuehai --repo ai-preview --pr 1 --review --format json
"""

import json
import sys
import os
from dataclasses import asdict

# 确保 Windows 终端 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import click

from src.config import print_config
from src.github.pr_capture import capture_pr_diff, summarize_diff
from src.github.client import _get_github as has_token
from src.ai.reviewer import review_pr_diff
from src.ai.types import ReviewResult


@click.command()
@click.option("--owner", required=True, help="GitHub 仓库所有者")
@click.option("--repo", required=True, help="仓库名")
@click.option("--pr", required=True, type=int, help="PR 编号")
@click.option("--format", "fmt", type=click.Choice(["json", "summary"]),
              default="json", help="输出格式")
@click.option("--review", is_flag=True, default=False,
              help="运行 AI 代码审查（需配置 DEEPSEEK_API_KEY）")
def cli(owner: str, repo: str, pr: int, fmt: str, review: bool):
    """从 GitHub 捕获指定 PR 数据，可选进行 AI 代码审查。"""

    # 显示配置状态
    print_config()
    click.echo()

    # 显示运行模式
    mode = "live" if has_token() else "mock"
    click.echo(f"[Mode: {mode}]")
    if mode == "mock":
        click.echo("[!] 未检测到 GitHub Token，将使用 Mock 数据。\n")

    # ========== AI 审查模式 ==========
    if review:
        click.echo(f"[*] 正在运行 AI 审查: {owner}/{repo}#{pr} ...\n")

        try:
            result = review_pr_diff(owner, repo, pr)

            if fmt == "json":
                click.echo(json.dumps(asdict(result), indent=2, ensure_ascii=False))
            else:
                click.echo(_format_review_markdown(result, owner, repo, pr))

            click.echo(
                f"\n[OK] 审查完成 | 风险等级: {result.overall_risk_level.upper()} | "
                f"风险项: {len(result.risk_items)} | 建议: {len(result.suggestions)}",
                err=True,
            )
        except Exception as e:
            click.echo(f"[FAIL] 审查失败: {e}", err=True)
            sys.exit(1)
        return

    # ========== Diff 捕获模式（原有行为） ==========
    click.echo(f"[*] 正在捕获 PR 数据: {owner}/{repo}#{pr} ...\n")

    try:
        result = capture_pr_diff(owner, repo, pr)

        if fmt == "summary":
            click.echo(summarize_diff(result.structured_diff))
            click.echo(f"\n[link] PR 链接: {result.pr.html_url}")
        else:
            click.echo(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))

        click.echo(
            f"\n[OK] 完成: {result.stats['files_changed']} 文件, "
            f"+{result.stats['additions']} -{result.stats['deletions']}",
            err=True,
        )
    except Exception as e:
        click.echo(f"[FAIL] 捕获失败: {e}", err=True)
        sys.exit(1)


def _format_review_markdown(
    result: ReviewResult, owner: str, repo: str, pr: int
) -> str:
    """将 ReviewResult 格式化为可读的 Markdown 审查报告。"""

    level = result.overall_risk_level.upper()
    level_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢", "NONE": "⚪"}
    icon = level_icon.get(level, "⚪")

    parts = [
        f"# AI Code Review: {owner}/{repo}#{pr}",
        "",
        f"**Risk Level:** {icon} {level}",
        f"**Risks:** {len(result.risk_items)} | **Suggestions:** {len(result.suggestions)}",
        "",
        "---",
        "",
        "## Summary",
        result.summary,
        "",
    ]

    # 风险分析
    if result.risk_items:
        parts.append("---")
        parts.append("")
        parts.append(f"## Risk Analysis ({len(result.risk_items)} items)")
        parts.append("")
        for r in result.risk_items:
            sev = r.severity.upper()
            parts.append(f"### [{sev}] {r.file}:{r.line_range} — {r.category}")
            parts.append(f"{r.description}")
            parts.append("")
            if r.code_snippet:
                parts.append("```python")
                parts.append(r.code_snippet.strip())
                parts.append("```")
                parts.append("")

    # 修复建议
    if result.suggestions:
        parts.append("---")
        parts.append("")
        parts.append(f"## Suggested Fixes ({len(result.suggestions)} items)")
        parts.append("")
        for s in result.suggestions:
            parts.append(f"### {s.file}:{s.line_range}")
            parts.append(f"**What:** {s.description}")
            parts.append("")
            if s.code_before:
                parts.append("**Before:**")
                parts.append("```python")
                parts.append(s.code_before.strip())
                parts.append("```")
                parts.append("")
            if s.code_after:
                parts.append("**After:**")
                parts.append("```python")
                parts.append(s.code_after.strip())
                parts.append("```")
                parts.append("")
            parts.append("---")
            parts.append("")

    # Meta
    model = result.meta.get("model", "unknown")
    tokens = result.meta.get("tokens_used", "N/A")
    parts.append(f"> Model: {model} | Tokens: {tokens}")

    return "\n".join(parts)


if __name__ == "__main__":
    cli()
