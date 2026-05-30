"""
应用配置模块 —— 从 .env 文件读取并校验环境变量。
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


@dataclass
class AppConfig:
    """应用配置，包含 API Token 等敏感信息。"""
    github_token: Optional[str]
    deepseek_api_key: Optional[str]


def get_config() -> AppConfig:
    """读取并返回类型安全的配置对象。缺失的值设为 None。"""
    github_token = os.getenv("GITHUB_ACCESS_TOKEN", "").strip() or None
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip() or None
    return AppConfig(github_token=github_token, deepseek_api_key=deepseek_api_key)


def _mask(value: Optional[str]) -> str:
    """脱敏处理：只显示前 8 位和后 4 位。"""
    if not value:
        return "(not set)"
    if len(value) <= 8:
        return "****"
    return value[:8] + "****..." + value[-4:]


def print_config() -> None:
    """打印当前配置状态（Token 脱敏）。"""
    config = get_config()
    print("=== AI PR Review Assistant -- Config Status ===")
    print(f"GitHub Token:      {_mask(config.github_token)} (valid: {config.github_token is not None})")
    print(f"DeepSeek API Key:  {_mask(config.deepseek_api_key)} (valid: {config.deepseek_api_key is not None})")
    print("==============================================")


if __name__ == "__main__":
    print_config()
