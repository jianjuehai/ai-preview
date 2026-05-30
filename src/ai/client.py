"""
DeepSeek API 客户端 —— 封装 OpenAI SDK 进行 DeepSeek 兼容的 chat completion 调用。
无 API Key 或请求失败时自动降级到本地 Mock 数据。
"""

import json
from pathlib import Path
from typing import Optional

from openai import OpenAI

from src.config import get_config

# Mock 数据文件路径
_MOCK_PATH = Path(__file__).resolve().parent.parent.parent / "tests" / "mock_data" / "sample_review.json"

# 缓存已加载的 mock 数据
_mock_cache: Optional[dict] = None


def _load_mock() -> dict:
    """加载 Mock AI 审查数据（带缓存）。"""
    global _mock_cache
    if _mock_cache is None:
        _mock_cache = json.loads(_MOCK_PATH.read_text(encoding="utf-8"))
    return _mock_cache


def _get_deepseek_client() -> Optional[OpenAI]:
    """获取 DeepSeek 客户端实例。Token 不可用时返回 None。"""
    config = get_config()
    if not config.deepseek_api_key:
        return None
    return OpenAI(
        api_key=config.deepseek_api_key,
        base_url="https://api.deepseek.com",
    )


# ====================================================================
# 公开 API
# ====================================================================

def chat_completion(messages: list[dict], **kwargs) -> dict:
    """
    向 DeepSeek 发送对话消息并返回解析后的响应 dict。

    参数:
        messages: 标准对话消息列表 [{"role": "system"|"user"|"assistant", "content": "..."}]
        **kwargs: 覆盖默认参数（model, temperature, max_tokens 等）

    返回:
        AI 响应的 JSON 解析结果（dict）。失败时返回 Mock 数据。

    降级条件:
        - 未配置 DeepSeek API Key
        - 网络错误
        - API 返回错误
        - 响应 JSON 解析失败
    """
    client = _get_deepseek_client()
    if client is None:
        print("[ai/client] No DeepSeek API key -- using mock data")
        return _load_mock()

    defaults = dict(
        model="deepseek-chat",
        temperature=0.3,
        max_tokens=4096,
    )
    defaults.update(kwargs)

    try:
        response = client.chat.completions.create(
            messages=messages,
            **defaults,
        )
        content = response.choices[0].message.content
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # AI 返回了非 JSON 内容，尝试从 markdown 代码块提取
                print("[ai/client] Response is not valid JSON -- attempting extraction")
                if "```json" in content:
                    block = content.split("```json")[1].split("```")[0]
                    return json.loads(block)
                if "```" in content:
                    block = content.split("```")[1].split("```")[0]
                    return json.loads(block)
                return {"summary": content, "risk_items": [], "suggestions": [], "meta": {"raw": True}}
        return {}
    except Exception as e:
        print(f"[ai/client] API error ({type(e).__name__}: {e}) -- falling back to mock data")
        return _load_mock()


# ====================================================================
# 开发调试入口
# ====================================================================
if __name__ == "__main__":
    import sys

    prompt = sys.argv[1] if len(sys.argv) > 1 else "Say hello in JSON: {\"greeting\": \"...\"}"

    result = chat_completion([
        {"role": "user", "content": prompt}
    ])
    print(json.dumps(result, indent=2, ensure_ascii=False))
