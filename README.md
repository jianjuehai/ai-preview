# AI PR Review Assistant

## 📖 项目简介

基于大模型与 Agent 架构的代码评审辅助工具，自动化分析 GitHub PR 变更，提供 **变更摘要**、**风险代码识别** 与 **智能修复建议**，配合可视化 Dashboard 直观呈现审查结果。

## 📖 演示视频

[▶ 点击观看演示视频](https://github.com/user-attachments/assets/fa44d3b4-76db-4008-8109-2ec49144aece)

## 🛠 技术栈

| 层级 | 技术 |
|---|---|
| 前端 Dashboard | Vue 3 + Vite + Vue Router + Prism.js |
| Web 服务 | FastAPI + Uvicorn |
| 核心逻辑 | Python 3.10+ |
| GitHub 集成 | PyGithub（自动 Mock 降级） |
| AI 审查 | DeepSeek V4（OpenAI 兼容 SDK，自动 Mock 降级） |
| CLI 工具 | Click |

## 🚀 快速启动

> **主分支始终保持可运行状态。** 未配置 API Key 时系统自动使用内置 Mock 数据运行。

### 1. 环境准备
- Python 3.10+ & pip
- Node.js 18+ & npm（仅 Dashboard 前端需要）

### 2. 安装依赖

```bash
git clone https://github.com/jianjuehai/ai-preview.git
cd ai-preview

# Python 后端
pip install -r requirements.txt

# Vue.js 前端（可选）
cd frontend && npm install && cd ..
```

### 3. 配置环境变量

编辑项目根目录的 `.env` 文件：

```env
GITHUB_ACCESS_TOKEN=<your_github_pat>
DEEPSEEK_API_KEY=<your_deepseek_api_key>
```

> Token 可选 —— 未配置时所有接口自动降级到 Mock 数据。

### 4. 启动

#### Web Dashboard（推荐）

```bash
# 终端 1：启动后端
python -m uvicorn src.api.server:app --port 8000

# 终端 2：启动前端
cd frontend && npm run dev
```

打开 **http://localhost:5173**，左侧文件列表 + 右侧语法高亮 Diff + AI 风险内联标注 + 修复建议面板。

#### CLI 模式

```bash
# Diff 捕获（Markdown 摘要）
python -m src.main --owner jianjuehai --repo ai-preview --pr 1 --format summary

# AI 代码审查（Markdown 报告）
python -m src.main --owner jianjuehai --repo ai-preview --pr 1 --review

# AI 代码审查（JSON）
python -m src.main --owner jianjuehai --repo ai-preview --pr 1 --review --format json
```

## 📂 项目结构

```
ai-preview/
├── src/
│   ├── config.py              # 环境变量配置 + Token 脱敏打印
│   ├── main.py                # CLI 入口（Click）
│   ├── github/                # PR 数据捕获模块
│   │   ├── types.py           # PrInfo, PrFile, DiffHunk, StructuredDiff ...
│   │   ├── client.py          # PyGithub 客户端 + Mock 降级
│   │   ├── diff_parser.py     # unified diff → 结构化数据
│   │   └── pr_capture.py      # capture_pr_diff() 编排器
│   ├── ai/                    # AI 智能分析模块
│   │   ├── types.py           # ReviewResult, RiskItem, Suggestion
│   │   ├── client.py          # DeepSeek API 客户端 + Mock 降级
│   │   ├── prompts.py         # System/User Prompt 模板
│   │   └── reviewer.py        # review_pr_diff() 编排器
│   └── api/                   # Web 服务
│       └── server.py          # FastAPI app + API 端点
├── frontend/                  # Vue.js Dashboard
│   ├── src/views/Dashboard.vue    # 双面板主布局
│   ├── src/components/
│   │   ├── FileList.vue           # 左面板：文件列表 + 风险指示
│   │   ├── DiffViewer.vue         # 右面板：Diff 代码渲染
│   │   ├── DiffLine.vue           # 单行 Diff + Prism 高亮 + 内联风险色条
│   │   └── SuggestionPanel.vue    # 修复建议（折叠/展开 + 拖拽调整大小）
│   └── src/utils/
│       ├── annotations.js         # line_range 解析与匹配
│       └── diffColors.js          # 配色映射
├── tests/                    # pytest 测试套件（63+ tests）
├── pyproject.toml
└── requirements.txt
```

## 🔌 API 端点

| 端点 | 方法 | 说明 |
|---|---|---|
| `/` | GET | Dashboard SPA（构建后）或占位页 |
| `/api/diff?owner=&repo=&pr=` | GET | PR 结构化 Diff 数据 |
| `/api/review?owner=&repo=&pr=` | GET | AI 审查结果 |
| `/docs` | GET | OpenAPI 交互文档 |

## 🧪 测试

```bash
# 全量 Python 测试
pytest tests/ -v

# 前端构建验证
cd frontend && npm run build
```

## 📐 设计原则

1. **增量开发** — 每个 PR 极小粒度，不跨层
2. **主干安全** — 未配置 Token 时自动 Mock 降级，main 始终可运行
3. **类型安全** — Python dataclass + JS 类型注解
4. **防御性编程** — AI JSON 输出缺失字段有默认值，不崩溃
