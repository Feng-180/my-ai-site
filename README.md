# 零撸情报局 | 白嫖资源自动化系统 v3.0

一个极客风的完全私密的「自动化白嫖」资源网站。采用前端 AES-256 解密架构，让你在保持 GitHub 仓库公开的情况下，也能实现数据的绝对私密。

![Version](https://img.shields.io/badge/version-3.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12-blue)

## ✨ 特性

- 🤖 **自动化抓取**: 从 Reddit、GitHub、Hacker News、Product Hunt 等多个渠道并发抓取
- 🔐 **高强度加密**: AES-256-CBC 加密，数据本地解密，隐私安全
- 🎨 **极客风 UI**: Cyberpunk 风格界面 + 资源搜索/过滤
- ⚡ **并发引擎**: ThreadPoolExecutor 多线程抓取，速度提升 3x
- 🔍 **实时搜索**: 内置 AI 羊毛搜集器，实时从互联网搜索最新白嫖信息
- 📱 **响应式设计**: 完美适配手机和桌面端

## 🏗️ 架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   数据抓取源    │ --> │  Python 爬虫    │ --> │  AES-256 加密   │
│ Reddit/GitHub   │     │  (scraper.py)   │     │  (data.enc)     │
│ HN/ProductHunt  │     │  并发 4 线程    │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         v
                                              ┌─────────────────┐
                                              │   GitHub Pages  │
                                              │   index.html    │
                                              │  collector.html │
                                              └─────────────────┘
                                                         │
                                                         v
                                              ┌─────────────────┐
                                              │   浏览器端解密  │
                                              │  搜索 + 过滤    │
                                              └─────────────────┘
```

## 📄 页面说明

| 页面 | 描述 |
|------|------|
| `index.html` | 主站 - 加密资源库，需要密钥解密查看 |
| `collector.html` | AI 羊毛搜集器 - 实时从互联网搜索白嫖信息 |

## 🚀 快速开始

### 1. 本地测试

```bash
# 克隆仓库
git clone https://github.com/Feng-180/my-ai-site.git
cd my-ai-site

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行爬虫 (使用默认密码测试)
python scraper.py
```

### 2. 修改默认密码

打开 `scraper.py`，修改默认密码：

```python
SECRET_KEY = os.getenv("SECRET_KEY", "你的复杂密码")
```

### 3. GitHub Actions 部署

1. 去你的 GitHub 仓库 -> **Settings** -> **Secrets and variables** -> **Actions**
2. 点击 **New repository secret**
3. **Name**: `SECRET_KEY`
4. **Secret**: `你的真实复杂密码`
5. 保存

### 4. 开启 GitHub Pages

- **Settings** -> **Pages**
- Source 选择 **Deploy from a branch**
- 分支选择 **main**，文件夹 **/(root)**
- 几分钟后站点上线

## 📦 数据源 (v3.0)

| 数据源 | 描述 | 资源数 |
|--------|------|--------|
| Free-for-Dev | GitHub 开发者白嫖清单 | 35+ |
| Reddit | eFreebies/Freebies 热门 | 30+ |
| GitHub Trending | 高星开源项目 | 20+ |
| AlternativeTo | 热门免费替代品 | 5+ |
| AI Resources | 免费 AI 工具汇总 (含 DeepSeek/Grok/Kimi) | 15+ |
| Virtual Goods | 虚拟货源精选 | 7+ |
| Product Hunt | 新兴免费产品 | 5+ |
| Hacker News | AI 相关热门项目 | 动态 |

## 🔧 手动运行

```bash
# 手动触发抓取
python scraper.py

# 提交更改
git add .
git commit -m "Update resources"
git push
```

## ⚠️ 注意事项

1. **密码安全**: 切勿将真实密码直接提交到代码中，使用 GitHub Secrets
2. **API 限制**: GitHub API 有速率限制，注意请求频率
3. **数据备份**: 定期备份 `data.enc` 文件

## 📄 许可证

MIT License - 欢迎贡献和改进！

## 🙏 致谢

- [ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev) - 开发者白嫖资源清单
- [CryptoJS](https://github.com/brix/crypto-js) - 前端加密库
- [Hacker News API](https://github.com/HackerNews/API) - HN 数据接口
