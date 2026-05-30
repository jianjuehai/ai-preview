# AI PR Review Assistant

## 📖 项目简介 (Project Overview)
本项目是一个基于大模型与 Agent 架构的代码评审辅助工具，旨在通过自动化分析 GitHub PR 变更，解决代码审查中缺乏上下文、耗时且容易漏掉深层风险的痛点。系统支持 PR 变更总结、风险代码识别与智能修复建议。

## 🛠 技术栈选型 (Tech Stack)
*   **前端交互:** Vue.js (用于构建直观的评审结果 Dashboard 或看板)
*   **核心逻辑 / Agent:**  Python
*   **AI 与工具链:** DeepSeek V4 API, Model Context Protocol (MCP) (用于扩展 Agent 能力，如读取文件、调用外部验证 API)
*   **其他关键技术:** [例如: AST 语法树分析、用于深度上下文的向量检索等]

## 🚀 快速启动 (Quick Start)
> **评委/审查者请注意**：主分支始终保持可运行状态。部分尚未完全接入后端 AI 接口的功能，目前采用 Mock 数据配合 Feature Flag 运行，不影响核心流程的演示。

### 环境准备
确保本地已安装 Python 3.10+ 及 pip。

### 1. 克隆 & 安装依赖
```bash
git clone https://github.com/jianjuehai/AI-PR-Review.git
cd AI-PR-Review
pip install -r requirements.txt
```

### 2. 配置环境变量
项目根目录已提供 `.env` 文件（已加入 `.gitignore`），请确保包含以下配置：
```env
GITHUB_ACCESS_TOKEN=<your_github_pat>
DEEPSEEK_API_KEY=<your_deepseek_api_key>
```

### 3. 验证配置
```bash
# 运行配置模块检查 Token 状态（自动脱敏）
python -m src.config
```

### 4. 运行（CLI 模式）
```bash
python -m src.main --owner <owner> --repo <repo> --pr <pr_number>
```
> 尚未配置真实 Token 时，系统自动使用 Mock 数据运行。