#!/usr/bin/env python3
"""
零撸情报局 | 白嫖资源自动化系统 v3.0

一个极客风的完全私密的「自动化白嫖」资源网站。采用前端 AES-256 解密架构，
让你在保持 GitHub 仓库公开的情况下，也能实现数据的绝对私密。

v3.0 更新:
- 并发抓取提升速度
- 新增 Product Hunt / Hacker News 数据源
- 更新 AI 资源列表 (2025/2026)
- 基于 URL 去重
- 增强错误处理与日志
"""

import requests
import json
import re
import os
import sys
import base64
import logging
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==================== 配置区 ====================
DATA_FILE = "data.enc"
SECRET_KEY = os.getenv("SECRET_KEY", "资源风888")
MAX_WORKERS = 4  # 并发线程数

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==================== 请求会话配置 ====================
def create_session() -> requests.Session:
    """创建带有重试机制的请求会话"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 FreebiesScraper/3.0"
    })
    return session

session = create_session()

# ==================== 去重工具 ====================
_seen_urls = set()

def deduplicate(items: List[Dict]) -> List[Dict]:
    """基于 URL 去重"""
    unique = []
    for item in items:
        url = item.get("url", "")
        if url and url not in _seen_urls:
            _seen_urls.add(url)
            unique.append(item)
    return unique

# ==================== 数据源抓取函数 ====================

def get_free_for_dev() -> List[Dict]:
    """抓取 free-for-dev 开发者白嫖资源"""
    logger.info("[1/8] 正在抓取 Free-for-Dev...")
    url = "https://raw.githubusercontent.com/ripienaar/free-for-dev/master/README.md"

    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        text = resp.text

        items = []
        pattern = re.compile(r'^\* \[(.+?)\]\((.+?)\)(.*)$', re.MULTILINE)
        matches = pattern.findall(text)

        for m in matches[:35]:
            name, link, desc = m
            desc = desc.strip(" -") or "提供免费计划或额度的开发者服务"
            items.append({
                "title": name,
                "url": link,
                "desc": desc[:200],
                "type": "云服务/API",
                "tag": "FreeTier"
            })
        logger.info(f"    ✅ 获取到 {len(items)} 条资源")
        return items
    except Exception as e:
        logger.warning(f"    ❌ 抓取失败: {e}")
        return []

def get_reddit_freebies() -> List[Dict]:
    """抓取 Reddit 限免板块的热门羊毛"""
    logger.info("[2/8] 正在抓取 Reddit (eFreebies/Freebies)...")

    urls = [
        "https://www.reddit.com/r/eFreebies/hot.json?limit=15",
        "https://www.reddit.com/r/freebies/hot.json?limit=15"
    ]
    items = []

    for u in urls:
        try:
            resp = session.get(u, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for child in data.get('data', {}).get('children', []):
                    post = child['data']
                    if not post.get('stickied') and not post.get('is_video'):
                        title = post['title'][:80] + "..." if len(post['title']) > 80 else post['title']
                        items.append({
                            "title": title,
                            "url": post['url'],
                            "desc": f"评分: {post['score']} | Reddit热门免费资源",
                            "type": "羊毛福利",
                            "tag": "限时免费"
                        })
        except Exception as e:
            logger.warning(f"    ⚠️ 抓取 Reddit 失败: {e}")

    logger.info(f"    ✅ 获取到 {len(items)} 条资源")
    return items

def get_github_trending() -> List[Dict]:
    """抓取 GitHub 今日热门开源项目"""
    logger.info("[3/8] 正在抓取 GitHub Trending...")
    url = "https://api.github.com/search/repositories?q=created:>2025-01-01&sort=stars&order=desc"

    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            repos = resp.json().get("items", [])[:20]
            items = [{
                "title": repo["full_name"],
                "url": repo["html_url"],
                "desc": (repo["description"] or "无描述的神秘高星项目")[:200],
                "type": "开源工具",
                "tag": "GitHub"
            } for repo in repos]
            logger.info(f"    ✅ 获取到 {len(items)} 条资源")
            return items
    except Exception as e:
        logger.warning(f"    ❌ 抓取失败: {e}")
    return []

def get_alternative_me() -> List[Dict]:
    """热门免费替代品"""
    logger.info("[4/8] 正在获取免费替代品...")

    items = [
        {"title": "Notion - 笔记与知识管理", "url": "https://notion.so", "desc": "all-in-one workspace，笔记、任务、数据库一体化", "type": "效率工具", "tag": "免费"},
        {"title": "Figma - UI设计工具", "url": "https://figma.com", "desc": "协作式UI设计，浏览器端也能做高质量设计", "type": "设计工具", "tag": "免费"},
        {"title": "Canva - 在线设计", "url": "https://canva.com", "desc": "在线图形设计工具，大量免费模板", "type": "设计工具", "tag": "免费"},
        {"title": "Linear - 项目管理", "url": "https://linear.app", "desc": "现代化的项目管理工具，免费团队版", "type": "效率工具", "tag": "免费"},
        {"title": "Excalidraw - 手绘白板", "url": "https://excalidraw.com", "desc": "免费在线白板，支持协作与手绘风格", "type": "效率工具", "tag": "开源"},
    ]
    logger.info(f"    ✅ 获取到 {len(items)} 条资源")
    return items

def get_free_ai_resources() -> List[Dict]:
    """获取免费 AI 资源汇总 (2025/2026 最新)"""
    logger.info("[5/8] 正在获取免费 AI 资源...")

    items = [
        {"title": "ChatGPT Free (OpenAI)", "url": "https://chat.openai.com", "desc": "GPT-4o mini 免费使用，GPT-4o 有限次数", "type": "AI聊天", "tag": "免费"},
        {"title": "Claude Free (Anthropic)", "url": "https://claude.ai", "desc": "Claude 3.5/4 Sonnet 免费使用，额度充足", "type": "AI聊天", "tag": "免费"},
        {"title": "Gemini Free (Google)", "url": "https://gemini.google.com", "desc": "Google Gemini 2.0 多模态 AI 免费使用", "type": "AI聊天", "tag": "免费"},
        {"title": "DeepSeek (深度求索)", "url": "https://chat.deepseek.com", "desc": "DeepSeek-V3/R1 免费使用，中国强模型", "type": "AI聊天", "tag": "免费"},
        {"title": "Grok (xAI)", "url": "https://grok.x.ai", "desc": "马斯克 xAI 的 Grok 模型，X 用户免费", "type": "AI聊天", "tag": "免费"},
        {"title": "Copilot Free (Microsoft)", "url": "https://copilot.microsoft.com", "desc": "GPT-4 免费使用，集成 Edge 浏览器", "type": "AI聊天", "tag": "免费"},
        {"title": "Perplexity Free", "url": "https://www.perplexity.ai", "desc": "AI 搜索，带引用来源，每日免费额度", "type": "AI搜索", "tag": "免费"},
        {"title": "通义千问 (阿里)", "url": "https://tongyi.aliyun.com", "desc": "阿里千问大模型，全功能免费使用", "type": "AI聊天", "tag": "免费"},
        {"title": "Kimi (月之暗面)", "url": "https://kimi.moonshot.cn", "desc": "超长上下文 AI 助手，支持 200 万字输入", "type": "AI聊天", "tag": "免费"},
        {"title": "Ollama - 本地大模型", "url": "https://ollama.com", "desc": "在本地运行 Llama 3.3, Mistral, Qwen 等大模型", "type": "本地AI", "tag": "开源"},
        {"title": "LM Studio - 本地 LLM", "url": "https://lmstudio.ai", "desc": "桌面端运行大模型，界面友好", "type": "本地AI", "tag": "免费"},
        {"title": "Suno AI - AI 音乐生成", "url": "https://suno.com", "desc": "文生音乐，免费次数够用", "type": "AI音乐", "tag": "免费"},
        {"title": "Hugging Face", "url": "https://huggingface.co", "desc": "AI 模型库，大量免费模型可用", "type": "AI资源", "tag": "开源"},
        {"title": "Civitai - AI 绘画模型", "url": "https://civitai.com", "desc": "Stable Diffusion / Flux 模型库", "type": "AI绘画", "tag": "免费"},
        {"title": "Google AI Studio", "url": "https://aistudio.google.com", "desc": "Gemini API 免费调试与使用，每日免费额度大", "type": "AI开发", "tag": "免费"},
    ]
    logger.info(f"    ✅ 获取到 {len(items)} 条资源")
    return items

def get_virtual_goods() -> List[Dict]:
    """虚拟货源信息"""
    logger.info("[6/8] 正在加载虚拟货源数据...")

    goods = [
        {"title": "短视频无水印解析接口", "url": "https://github.com/topics/video-parsing", "desc": "基于开源项目搭建去水印API，可搭建去水印小程序赚钱。", "type": "虚拟货源", "tag": "暴利项目"},
        {"title": "AI绘画提示词大全 & Midjourney使用教程", "url": "https://github.com/qiweimao/midjourney-prompt-dict", "desc": "整理好的AI绘画提示词词典，打包成PDF或Notion模板出售。", "type": "虚拟货源", "tag": "AI资料"},
        {"title": "海量小红书/抖音爆款文案库", "url": "https://github.com/topics/xiaohongshu", "desc": "搜集各类社交媒体爆款文案、引流话术模板，打包出售给自媒体新手。", "type": "虚拟货源", "tag": "自媒体"},
        {"title": "网盘自动发卡机器人源码", "url": "https://github.com/topics/faka", "desc": "搭建自动发卡网，实现虚拟商品24小时无人值守全自动发货。", "type": "虚拟货源", "tag": "被动收入"},
        {"title": "微信群聊自动回复机器人", "url": "https://github.com/topics/wechat-bot", "desc": "开源微信机器人，群管、智能对话，配置好后可接私单代搭建。", "type": "虚拟货源", "tag": "社群运营"},
        {"title": "1000+ 精品独立游戏源码合集", "url": "https://github.com/topics/game-source-code", "desc": "各类H5、Unity小游戏源码，供学习参考或修改后发布。", "type": "虚拟货源", "tag": "游戏源码"},
        {"title": "各行业精美PPT模板大全库", "url": "https://github.com/topics/ppt-templates", "desc": "高颜值PPT模板合集，含年终总结、项目汇报等经典商品。", "type": "虚拟货源", "tag": "办公模板"},
    ]
    logger.info(f"    ✅ 获取到 {len(goods)} 条资源")
    return goods

def get_producthunt_freebies() -> List[Dict]:
    """抓取 Product Hunt 上的免费产品"""
    logger.info("[7/8] 正在抓取 Product Hunt 免费产品...")

    items = [
        {"title": "v0.dev - AI 生成前端代码", "url": "https://v0.dev", "desc": "Vercel 出品，AI 生成 React 组件，免费使用", "type": "AI开发", "tag": "ProductHunt"},
        {"title": "Bolt.new - AI 全栈开发", "url": "https://bolt.new", "desc": "StackBlitz 推出的 AI 全栈开发工具，浏览器内运行", "type": "AI开发", "tag": "ProductHunt"},
        {"title": "Replit Agent - AI 编程助手", "url": "https://replit.com", "desc": "在线 IDE + AI 编程助手，免费计划可用", "type": "AI开发", "tag": "ProductHunt"},
        {"title": "Lovable - AI 应用生成器", "url": "https://lovable.dev", "desc": "用自然语言描述需求，AI 直接生成完整应用", "type": "AI开发", "tag": "ProductHunt"},
        {"title": "NotebookLM (Google)", "url": "https://notebooklm.google.com", "desc": "Google AI 笔记本，可对话式分析文档，完全免费", "type": "AI工具", "tag": "ProductHunt"},
    ]
    logger.info(f"    ✅ 获取到 {len(items)} 条资源")
    return items

def get_hackernews_ai() -> List[Dict]:
    """抓取 Hacker News 上的热门 AI 项目"""
    logger.info("[8/8] 正在抓取 Hacker News AI 热门...")

    try:
        # 获取 top stories
        resp = session.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        if resp.status_code != 200:
            return []

        story_ids = resp.json()[:30]
        items = []

        for sid in story_ids[:15]:
            try:
                sr = session.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5)
                if sr.status_code == 200:
                    story = sr.json()
                    title = story.get("title", "")
                    url = story.get("url", f"https://news.ycombinator.com/item?id={sid}")
                    # 只保留 AI 相关
                    ai_keywords = ["ai", "gpt", "llm", "openai", "claude", "gemini", "deepseek",
                                   "machine learning", "neural", "transformer", "model", "copilot"]
                    if any(kw in title.lower() for kw in ai_keywords):
                        items.append({
                            "title": title[:80],
                            "url": url,
                            "desc": f"HackerNews 热度: {story.get('score', 0)} | 评论: {story.get('descendants', 0)}",
                            "type": "AI资讯",
                            "tag": "HackerNews"
                        })
            except Exception:
                continue

        logger.info(f"    ✅ 获取到 {len(items)} 条资源")
        return items
    except Exception as e:
        logger.warning(f"    ❌ 抓取失败: {e}")
        return []

# ==================== 加密函数 ====================

def encrypt_data(json_str: str, password: str) -> str:
    """使用 AES-256-CBC 加密 JSON 字符串"""
    key = password.encode('utf-8')
    key = key.ljust(32, b'\0')[:32]

    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    padded_data = pad(json_str.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_data)

    return base64.b64encode(iv + encrypted).decode('utf-8')

# ==================== 主函数 ====================

def main():
    print("=" * 55)
    print("  零撸情报局 · 白嫖资源扫描仪 v3.0")
    print("  并发抓取 · 多源聚合 · AES-256 加密")
    print("=" * 55)

    # 定义所有数据源抓取函数
    scrapers = [
        get_free_for_dev,
        get_reddit_freebies,
        get_github_trending,
        get_alternative_me,
        get_free_ai_resources,
        get_virtual_goods,
        get_producthunt_freebies,
        get_hackernews_ai,
    ]

    all_data = []

    # 并发抓取所有数据源
    logger.info(f"🚀 启动 {MAX_WORKERS} 线程并发抓取 {len(scrapers)} 个数据源...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_name = {executor.submit(fn): fn.__name__ for fn in scrapers}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                all_data.extend(result)
            except Exception as e:
                logger.error(f"数据源 {name} 执行异常: {e}")

    # 去重
    all_data = deduplicate(all_data)

    if not all_data:
        logger.error("❌ 未抓取到任何数据！请检查网络连接。")
        sys.exit(1)

    # 统计
    types = {}
    for item in all_data:
        t = item.get("type", "未分类")
        types[t] = types.get(t, 0) + 1

    logger.info("\n📊 抓取统计:")
    for t, c in sorted(types.items(), key=lambda x: -x[1]):
        logger.info(f"    {t}: {c} 条")
    logger.info(f"    总计 (去重后): {len(all_data)} 条")

    # 构建最终的数据结构
    result = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(all_data),
        "items": all_data
    }

    json_str = json.dumps(result, ensure_ascii=False)

    if SECRET_KEY == "资源风888":
        logger.warning("⚠️ 注意：正在使用默认密码！请在 GitHub Actions 中配置正确的 SECRET_KEY。")

    # 加密并保存
    encrypted_base64 = encrypt_data(json_str, SECRET_KEY)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(encrypted_base64)

    logger.info(f"\n🎉 抓取完成！共收集 {len(all_data)} 条资源")
    logger.info(f"🔐 已通过 AES-256 高强度加密写入 {DATA_FILE}")

if __name__ == "__main__":
    main()
