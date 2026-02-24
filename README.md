# 零撸情报局 | 白嫖资源自动化系统

一个极客风的完全私密的「自动化白嫖」资源网站。采用前端 AES-256 解密架构，让你在保持 GitHub 仓库公开的情况下，也能实现数据的绝对私密（别人没有你的密码就只能看到一堆乱码）。

## 核心机制
- **Python 爬虫**: 自动从 Reddit、GitHub、开源合集等渠道抓取最新的免费额度、限免福利、开源平替。
- **高强度加密**: 爬虫不会把抓到的数据明文存放到仓库。它会使用 `AES-256-CBC` 将其加密并保存为 `data.enc`。
- **本地化解密**: 浏览网页时，你输入的密码不会发送到任何服务器，而是直接用 JS 在你本地设备上解密 `data.enc`。即使有人看到你的网址，没有密码也无济于事。

## 如何部署和配置？

### 1. 修改 Python 代码中的密码（本地测试用）
打开 `scraper.py`，把：
`SECRET_KEY = os.getenv("SECRET_KEY", "你的默认测试密码")`
换成你想要的复杂密码（例如：`MySuperSecretKey888`）。

### 2. 在 GitHub 配置密码 (GitHub Actions)
如果直接把真实密码写在代码里，别人就能看到代码里的密码。所以我们利用 GitHub Secrets 隐藏密码。
- 去你的 GitHub 仓库页面 -> **Settings** -> **Secrets and variables** -> **Actions**
- 点击 **New repository secret**
- **Name** 填写：`SECRET_KEY`
- **Secret** 填写：`你的真实复杂密码`
- 保存。这样 GitHub Actions 每天运行时，就会提取这个密码去加密抓取到的数据！

### 3. 开启 GitHub Pages
- 去 **Settings** -> **Pages**
- Source 选择 **Deploy from a branch**，分支选择 **main**，文件夹 **/(root)**。
- 几分钟后，你的站点就会上线。

### 4. 每日自动更新
`.github/workflows/update.yml` 已配置为每天自动抓取 2 次并推送加密数据。你也可以在 Actions 面板手动点击运行。

## ⚠️ 隐私声明
你的解密密钥非常重要，它是能看到数据的唯一凭证，**永远不要把它直接提交到代码仓库中**，请务必使用 GitHub Actions Secret。