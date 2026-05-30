"""
AI 代码审查相关类型定义 —— 使用 dataclass 提供类型安全的数据结构。
"""

from dataclasses import dataclass, field
from typing import Optional, Literal

Severity = Literal["critical", "high", "medium", "low"]


@dataclass
class RiskItem:
    """单个代码风险项。"""
    file: str                 # 文件名
    line_range: str           # 如 "L12-L15"
    severity: Severity        # 严重程度
    category: str             # 分类：security, bug, performance, style, maintainability, logic
    description: str          # 风险描述
    code_snippet: str         # 问题代码片段


@dataclass
class Suggestion:
    """单个修复建议。"""
    file: str
    line_range: str
    description: str          # 改什么、为什么
    code_before: Optional[str] = None  # 当前代码
    code_after: Optional[str] = None   # 建议替换


@dataclass
class ReviewResult:
    """完整 AI 审查输出。"""
    summary: str                              # 2-3 段 PR 变更摘要
    risk_items: list[RiskItem] = field(default_factory=list)
    suggestions: list[Suggestion] = field(default_factory=list)
    meta: dict = field(default_factory=dict)  # model, tokens_used 等

    @property
    def overall_risk_level(self) -> str:
        """最高风险等级，无风险时返回 'none'。"""
        order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        if not self.risk_items:
            return "none"
        return max(self.risk_items, key=lambda r: order.get(r.severity, 0)).severity

    def risks_by_severity(self) -> dict:
        """按严重程度分组统计。"""
        counts: dict[str, int] = {}
        for r in self.risk_items:
            counts[r.severity] = counts.get(r.severity, 0) + 1
        return counts
