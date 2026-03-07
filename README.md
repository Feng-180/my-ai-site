# 零撸情报局 · AI 白嫖资源实时面板

实时聚合全网 AI 免费资源。自动抓取 + 浏览器实时获取，5 大分类，高级 UI。

![版本](https://img.shields.io/badge/版本-4.0-818cf8)
![许可证](https://img.shields.io/badge/许可证-MIT-34d399)
![Python](https://img.shields.io/badge/Python-3.12-fbbf24)

## ✨ 特性

- 🤖 **实时数据面板**: 浏览器端直接调用 GitHub / Hacker News API 获取最新数据
- 📦 **缓存补充**: GitHub Actions 每日自动抓取 Reddit / free-for-dev 等源
- 🔍 **全文搜索**: 实时过滤资源标题、描述、标签
- 🎨 **高级 UI**: 玻璃拟态 + 深色主题 + 渐变动画 + 响应式设计
- 📊 **5 大分类**: AI 工具 / 免费 API / 教育认证 / 开发资源 / AI 资讯
- ⚡ **搜集器**: 内置 AI 羊毛搜集器，并发搜索全网白嫖信息

## 🏗️ 架构

```
实时获取（浏览器端）          缓存获取（GitHub Actions）
┌──────────────┐            ┌──────────────┐
│ GitHub API   │            │ Reddit       │
│ HN API       │ ──┐       │ free-for-dev │ ── scraper.py
│ free-for-dev │   │       │ HN / GitHub  │        │
└──────────────┘   │       └──────────────┘        │
                   ▼                                ▼
            ┌─────────────────────────────────┐
            │         index.html              │
            │    5 分类 · 搜索 · 实时面板      │
            └─────────────────────────────────┘
                         │
            ┌─────────────────────────────────┐
            │       collector.html            │
            │   DuckDuckGo 并发搜索聚合        │
            └─────────────────────────────────┘
```

## 📄 页面

| 页面 | 功能 |
|------|------|
| `index.html` | 主站 · 实时数据面板，5 大分类展示 |
| `collector.html` | AI 羊毛搜集器 · 全网并发搜索 |

## 🚀 快速开始

```bash
# 克隆
git clone https://github.com/Feng-180/my-ai-site.git
cd my-ai-site

# 安装依赖
pip install -r requirements.txt

# 运行爬虫生成 data.json
python scraper.py
```

## 📦 数据源

| 数据源 | 类型 | 分类 |
|--------|------|------|
| 精选资源 | 人工维护 | AI 工具 / API / 教育 |
| GitHub API | 实时 | 开发资源 |
| Hacker News | 实时 | AI 资讯 |
| free-for-dev | 实时/缓存 | 开发资源 |
| Reddit | 缓存 | AI 资讯 |

## ⚠️ 注意

- GitHub API 有速率限制，未认证每小时 60 次
- `data.json` 由 GitHub Actions 每日自动更新

## 📄 许可证

MIT License
