#!/usr/bin/env python3
"""
AI PR Review Assistant — CLI 入口

用法：
    python -m src.main --owner <owner> --repo <repo> --pr <number>
    python -m src.main --owner jianjuehai --repo ai-preview --pr 1
    python -m src.main --owner jianjuehai --repo ai-preview --pr 1 --format summary
"""

import json
import sys
import os

# 确保 Windows 终端 UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import click

from src.config import print_config
from src.github.pr_capture import capture_pr_diff, summarize_diff
from src.github.client import _get_github as has_token


@click.command()
@click.option("--owner", required=True, help="GitHub 仓库所有者")
@click.option("--repo", required=True, help="仓库名")
@click.option("--pr", required=True, type=int, help="PR 编号")
@click.option("--format", "fmt", type=click.Choice(["json", "summary"]), default="json", help="输出格式")
def cli(owner: str, repo: str, pr: int, fmt: str):
    """从 GitHub 捕获指定 PR 的完整数据与结构化 Diff。"""

    # 显示配置状态
    print_config()
    click.echo()

    # 显示运行模式
    mode = "live" if has_token() else "mock"
    click.echo(f"[Mode: {mode}]")
    if mode == "mock":
        click.echo("[!] 未检测到 GitHub Token，将使用 Mock 数据。\n")

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


if __name__ == "__main__":
    cli()
