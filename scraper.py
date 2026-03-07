#!/usr/bin/env python3
"""
零撸情报局 · 白嫖资源自动抓取系统 v4.0

功能:
- 从 GitHub、Reddit、Hacker News、free-for-dev 等数据源自动抓取
- 输出明文 data.json 供前端直接读取
- 并发抓取 + URL 去重 + 分类标注
- 高质量 AI 精选资源（中文）

分类:
- ai   : AI 工具
- api  : 免费 API
- edu  : 教育认证
- dev  : 开发资源
- news : AI 资讯
"""

import requests
import json
import re
import os
import sys
import logging
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==================== 配置 ====================
DATA_FILE = "data.json"
MAX_WORKERS = 4

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==================== 请求会话 ====================
def create_session() -> requests.Session:
    """创建带重试机制的请求会话"""
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 零撸情报局/4.0"
    })
    return session

session = create_session()

# ==================== 去重 ====================
_seen = set()

def dedup(items: List[Dict]) -> List[Dict]:
    """基于 URL 去重"""
    out = []
    for it in items:
        url = it.get("url", "")
        if url and url not in _seen:
            _seen.add(url)
            out.append(it)
    return out

# ==================== 数据源 ====================

def 抓取_free_for_dev() -> List[Dict]:
    """从 free-for-dev 抓取开发者免费资源（仅 AI/云/API 相关）"""
    logger.info("[1/5] 正在抓取 free-for-dev 开发者资源...")
    try:
        resp = session.get(
            "https://raw.githubusercontent.com/ripienaar/free-for-dev/master/README.md",
            timeout=15
        )
        resp.raise_for_status()

        items = []
        pattern = re.compile(r'^\* \[(.+?)\]\((.+?)\)(.*)$', re.MULTILINE)
        ai_kws = ['ai', 'ml', 'api', 'cloud', 'deploy', 'database', 'hosting',
                   'serverless', 'monitor', 'gpu', 'inference']

        for m in pattern.finditer(resp.text):
            name, url, raw_desc = m.groups()
            desc = raw_desc.strip(" -") or "提供免费计划的开发者服务"
            if any(k in (name + desc).lower() for k in ai_kws):
                items.append({
                    "title": name,
                    "url": url,
                    "desc": desc[:180],
                    "category": "dev",
                    "tag": "免费套餐",
                    "source": "free-for-dev"
                })
            if len(items) >= 30:
                break

        logger.info(f"    ✅ 获取 {len(items)} 条")
        return items
    except Exception as e:
        logger.warning(f"    ❌ 失败: {e}")
        return []

def 抓取_reddit() -> List[Dict]:
    """从 Reddit 抓取免费资源"""
    logger.info("[2/5] 正在抓取 Reddit 免费资源...")
    urls = [
        "https://www.reddit.com/r/eFreebies/hot.json?limit=15",
        "https://www.reddit.com/r/freebies/hot.json?limit=10",
    ]
    items = []
    for u in urls:
        try:
            resp = session.get(u, timeout=10)
            if resp.status_code == 200:
                for child in resp.json().get('data', {}).get('children', []):
                    post = child['data']
                    if post.get('stickied') or post.get('is_video'):
                        continue
                    title = post['title']
                    if len(title) > 80:
                        title = title[:80] + "..."
                    items.append({
                        "title": title,
                        "url": post['url'],
                        "desc": f"Reddit 热度 {post['score']} · 免费资源分享",
                        "category": "news",
                        "tag": "限时免费",
                        "source": "Reddit"
                    })
        except Exception as e:
            logger.warning(f"    ⚠️ Reddit 失败: {e}")

    logger.info(f"    ✅ 获取 {len(items)} 条")
    return items

def 抓取_github_trending() -> List[Dict]:
    """从 GitHub API 获取 AI 热门开源项目"""
    logger.info("[3/5] 正在抓取 GitHub AI 热门项目...")
    try:
        resp = session.get(
            "https://api.github.com/search/repositories?q=topic:ai+topic:llm+stars:>500&sort=updated&order=desc&per_page=20",
            timeout=10
        )
        if resp.status_code != 200:
            return []

        items = []
        for repo in resp.json().get("items", []):
            desc = repo.get("description") or "暂无描述"
            items.append({
                "title": repo["full_name"],
                "url": repo["html_url"],
                "desc": desc[:200],
                "category": "dev",
                "tag": f"⭐ {repo['stargazers_count']:,}",
                "source": "GitHub"
            })

        logger.info(f"    ✅ 获取 {len(items)} 条")
        return items
    except Exception as e:
        logger.warning(f"    ❌ 失败: {e}")
        return []

def 抓取_hackernews() -> List[Dict]:
    """从 Hacker News 获取 AI 相关热门"""
    logger.info("[4/5] 正在抓取 Hacker News AI 资讯...")
    try:
        resp = session.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=8)
        if resp.status_code != 200:
            return []

        ids = resp.json()[:40]
        ai_kws = ['ai', 'gpt', 'llm', 'openai', 'claude', 'gemini', 'deepseek',
                   'model', 'transformer', 'copilot', 'anthropic', 'agent', 'mlops']
        items = []

        for sid in ids:
            try:
                sr = session.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5)
                if sr.status_code != 200:
                    continue
                story = sr.json()
                title = story.get("title", "")
                if any(k in title.lower() for k in ai_kws):
                    items.append({
                        "title": title[:80],
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "desc": f"HN 热度 {story.get('score', 0)} · 评论 {story.get('descendants', 0)}",
                        "category": "news",
                        "tag": "热门",
                        "source": "Hacker News"
                    })
                if len(items) >= 15:
                    break
            except Exception:
                continue

        logger.info(f"    ✅ 获取 {len(items)} 条")
        return items
    except Exception as e:
        logger.warning(f"    ❌ 失败: {e}")
        return []

def 精选资源() -> List[Dict]:
    """高质量中文精选资源（人工维护）"""
    logger.info("[5/5] 正在加载精选资源...")

    items = [
        # === AI 工具 ===
        {"title": "ChatGPT", "url": "https://chat.openai.com", "desc": "OpenAI 旗舰聊天 AI，GPT-4o mini 完全免费，GPT-4o 有限次数可用", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Claude", "url": "https://claude.ai", "desc": "Anthropic 出品，Claude 3.5/4 Sonnet 免费使用，长上下文能力优秀", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Gemini", "url": "https://gemini.google.com", "desc": "Google 多模态 AI，Gemini 2.0 免费使用，支持图片/代码/搜索", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "DeepSeek", "url": "https://chat.deepseek.com", "desc": "深度求索 DeepSeek-V3/R1 完全免费，中国最强开源模型", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Grok", "url": "https://grok.x.ai", "desc": "马斯克 xAI 的 Grok，X 用户免费，支持实时搜索", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Copilot", "url": "https://copilot.microsoft.com", "desc": "微软 AI 助手，基于 GPT-4，免费使用，集成必应和 DALL-E", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Perplexity", "url": "https://www.perplexity.ai", "desc": "AI 搜索引擎，带引用来源，每日免费 Pro 搜索额度", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "通义千问", "url": "https://tongyi.aliyun.com", "desc": "阿里千问大模型，对话/写作/编程/图片理解全功能免费", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Kimi", "url": "https://kimi.moonshot.cn", "desc": "月之暗面出品，200 万字超长上下文，文件分析能力极强", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Ollama", "url": "https://ollama.com", "desc": "本地运行 Llama 3.3/Qwen/Mistral，完全离线隐私安全", "category": "ai", "tag": "开源", "source": "精选"},
        {"title": "NotebookLM", "url": "https://notebooklm.google.com", "desc": "Google AI 笔记本，文档分析+播客生成，完全免费", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Suno AI", "url": "https://suno.com", "desc": "AI 音乐生成，输入文字生成完整歌曲含人声，每日免费", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Poe", "url": "https://poe.com", "desc": "Quora 推出的 AI 聚合平台，一站式使用多种大模型，每日免费额度", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "智谱清言 (GLM)", "url": "https://chatglm.cn", "desc": "智谱 AI 出品，GLM-4 免费使用，支持联网搜索和文件分析", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "豆包", "url": "https://www.doubao.com", "desc": "字节跳动 AI 助手，基于云雀大模型，对话/创作/知识问答完全免费", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Character.AI", "url": "https://character.ai", "desc": "AI 角色扮演平台，可与定制虚拟角色对话，免费使用", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "零一万物 (Yi)", "url": "https://www.lingyiwanwu.com", "desc": "李开复创立，Yi-Large 免费试用，中英文能力均衡", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "Midjourney", "url": "https://www.midjourney.com", "desc": "顶级 AI 绘画工具，通过 Discord 使用，新用户可免费试用", "category": "ai", "tag": "试用", "source": "精选"},
        {"title": "Stable Diffusion WebUI", "url": "https://github.com/AUTOMATIC1111/stable-diffusion-webui", "desc": "开源 AI 绘画，本地运行完全免费，社区生态丰富", "category": "ai", "tag": "开源", "source": "精选"},
        {"title": "Windsurf", "url": "https://codeium.com/windsurf", "desc": "Codeium AI 编程 IDE，免费版代码补全和 AI Chat 无限使用", "category": "ai", "tag": "免费", "source": "精选"},
        {"title": "v0.dev", "url": "https://v0.dev", "desc": "Vercel AI 前端代码生成器，描述需求即可生成 React/HTML 代码", "category": "ai", "tag": "免费", "source": "精选"},

        # === 免费 API ===
        {"title": "Google AI Studio", "url": "https://aistudio.google.com", "desc": "Gemini API 免费调用，每分钟 15 次请求，免费额度极大方", "category": "api", "tag": "免费 API", "source": "精选"},
        {"title": "DeepSeek API", "url": "https://platform.deepseek.com", "desc": "注册即送免费 API 额度，性价比极高", "category": "api", "tag": "免费额度", "source": "精选"},
        {"title": "Groq API", "url": "https://console.groq.com", "desc": "超高速推理平台，Llama/Mixtral 免费调用，推理极快", "category": "api", "tag": "免费 API", "source": "精选"},
        {"title": "Cloudflare Workers AI", "url": "https://developers.cloudflare.com/workers-ai/", "desc": "每日 1 万次免费推理请求，部署简单", "category": "api", "tag": "免费 API", "source": "精选"},
        {"title": "Hugging Face", "url": "https://huggingface.co", "desc": "AI 模型库和推理 API，大量免费模型可直接调用", "category": "api", "tag": "开源", "source": "精选"},
        {"title": "通义千问 API", "url": "https://dashscope.aliyun.com", "desc": "阿里灵积平台，注册送百万 Token 免费额度", "category": "api", "tag": "免费额度", "source": "精选"},
        {"title": "Coze (扣子)", "url": "https://www.coze.com", "desc": "字节跳动 AI 开发平台，免费搭建 Bot 调用多种大模型", "category": "api", "tag": "免费", "source": "精选"},
        {"title": "Mistral API", "url": "https://console.mistral.ai", "desc": "注册即获免费额度，支持多种开源模型", "category": "api", "tag": "免费额度", "source": "精选"},
        {"title": "OpenRouter", "url": "https://openrouter.ai", "desc": "AI API 聚合网关，统一接口调用 100+ 模型，部分免费", "category": "api", "tag": "聚合 API", "source": "精选"},
        {"title": "Together AI", "url": "https://www.together.ai", "desc": "开源模型云端推理，注册送 $25 免费额度", "category": "api", "tag": "免费额度", "source": "精选"},
        {"title": "硅基流动 (SiliconFlow)", "url": "https://siliconflow.cn", "desc": "国内 AI 推理加速平台，注册送免费额度，支持多种模型", "category": "api", "tag": "免费额度", "source": "精选"},
        {"title": "智谱 API", "url": "https://open.bigmodel.cn", "desc": "智谱 AI 开放平台，注册送免费 Token，GLM-4 全线可用", "category": "api", "tag": "免费额度", "source": "精选"},

        # === 教育认证 ===
        {"title": "ChatGPT Plus 大兵认证", "url": "https://chat.openai.com", "desc": "通过美国军人身份验证可免费获得 ChatGPT Plus 订阅", "category": "edu", "tag": "认证白嫖", "source": "精选"},
        {"title": "Gemini Advanced 学生认证", "url": "https://one.google.com", "desc": "Google One AI Premium 学生版免费，含 Gemini Advanced 和 2TB", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "GitHub Education 学生包", "url": "https://education.github.com/pack", "desc": "含 Copilot 免费、Azure 额度、JetBrains 全家桶等数十项福利", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "JetBrains 学生认证", "url": "https://www.jetbrains.com/community/education/", "desc": "全部 IDE 免费（IntelliJ/PyCharm/WebStorm 等），需教育邮箱", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "Azure 学生订阅", "url": "https://azure.microsoft.com/free/students/", "desc": "无需信用卡，$100 AI 额度 + 免费云服务", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "Cursor Pro 学生认证", "url": "https://cursor.com", "desc": "AI 编程编辑器学生版免费 Pro 功能", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "Notion 教育版", "url": "https://www.notion.so/product/notion-for-education", "desc": "Notion Plus 教育版免费，含 Notion AI", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "AWS Educate", "url": "https://aws.amazon.com/education/awseducate/", "desc": "Amazon 云教育项目，免费 AWS 云服务和 AI 工具体验", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "Autodesk 学生版", "url": "https://www.autodesk.com/education/free-software/featured", "desc": "AutoCAD/Maya/3ds Max 等专业软件教育免费一年", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "1Password 学生版", "url": "https://1password.com/students", "desc": "专业密码管理器学生版免费，保护 API Key 安全", "category": "edu", "tag": "学生优惠", "source": "精选"},
        {"title": "Figma 教育版", "url": "https://www.figma.com/education/", "desc": "Figma 专业版教育免费，含 AI 设计功能", "category": "edu", "tag": "学生优惠", "source": "精选"},
    ]

    logger.info(f"    ✅ 加载 {len(items)} 条精选资源")
    return items

# ==================== 主函数 ====================
def main():
    print("=" * 55)
    print("  零撸情报局 · 白嫖资源扫描仪 v4.0")
    print("  并发抓取 · 多源聚合 · 明文 JSON")
    print("=" * 55)

    # 所有抓取函数
    scrapers = [
        抓取_free_for_dev,
        抓取_reddit,
        抓取_github_trending,
        抓取_hackernews,
        精选资源,
    ]

    all_data = []

    # 并发抓取
    logger.info(f"🚀 启动 {MAX_WORKERS} 线程并发抓取 {len(scrapers)} 个数据源...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fn): fn.__name__ for fn in scrapers}
        for future in as_completed(futures):
            name = futures[future]
            try:
                all_data.extend(future.result())
            except Exception as e:
                logger.error(f"数据源 {name} 异常: {e}")

    # 去重
    all_data = dedup(all_data)

    if not all_data:
        logger.error("❌ 未抓取到任何数据！")
        sys.exit(1)

    # 统计
    cats = {}
    for it in all_data:
        c = it.get("category", "未分类")
        cats[c] = cats.get(c, 0) + 1

    logger.info("\n📊 抓取统计:")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        logger.info(f"    {c}: {n} 条")
    logger.info(f"    总计: {len(all_data)} 条")

    # 构建 JSON
    result = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(all_data),
        "items": all_data
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(f"\n🎉 完成！已写入 {DATA_FILE} ({len(all_data)} 条资源)")

if __name__ == "__main__":
    main()
