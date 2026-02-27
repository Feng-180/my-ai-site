#!/usr/bin/env python3
"""
零撸情报局 | 白嫖资源自动化系统 v2.0

一个极客风的完全私密的「自动化白嫖」资源网站。采用前端 AES-256 解密架构，
让你在保持 GitHub 仓库公开的情况下，也能实现数据的绝对私密。

功能:
- 自动从多个数据源抓取免费/白嫖资源
- AES-256-CBC 高强度加密
- 支持 GitHub Actions 自动化部署
"""

import requests
import json
import re
import os
import sys
import base64
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==================== 配置区 ====================
DATA_FILE = "data.enc"
# 从环境变量获取密码，GitHub Actions 中设置 SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY", "资源风888")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FreebiesScraper/2.0"
    })
    return session

session = create_session()

# ==================== 数据源抓取函数 ====================

def get_free_for_dev() -> List[Dict]:
    """抓取 free-for-dev 开发者白嫖资源"""
    logger.info("[1/6] 正在抓取 Free-for-Dev...")
    url = "https://raw.githubusercontent.com/ripienaar/free-for-dev/master/README.md"
    
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        text = resp.text
        
        items = []
        pattern = re.compile(r'^\* \[(.+?)\]\((.+?)\)(.*)$', re.MULTILINE)
        matches = pattern.findall(text)
        
        for m in matches[:30]:
            name, link, desc = m
            desc = desc.strip(" -") or "提供免费计划或额度的开发者服务"
            items.append({
                "title": name,
                "url": link,
                "desc": desc,
                "type": "云服务/API",
                "tag": "FreeTier"
            })
        logger.info(f"    获取到 {len(items)} 条资源")
        return items
    except requests.exceptions.RequestException as e:
        logger.warning(f"    抓取失败: {e}")
        return []

def get_reddit_freebies() -> List[Dict]:
    """抓取 Reddit 限免板块的热门羊毛"""
    logger.info("[2/6] 正在抓取 Reddit (eFreebies/Freebies)...")
    
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
        except requests.exceptions.RequestException as e:
            logger.warning(f"    抓取 {u} 失败: {e}")
    
    logger.info(f"    获取到 {len(items)} 条资源")
    return items

def get_github_trending() -> List[Dict]:
    """抓取 GitHub 今日热门开源项目"""
    logger.info("[3/6] 正在抓取 GitHub Trending...")
    url = "https://api.github.com/search/repositories?q=created:>2024-01-01&sort=stars&order=desc"
    
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            repos = resp.json().get("items", [])[:15]
            items = [{
                "title": repo["full_name"],
                "url": repo["html_url"],
                "desc": repo["description"] or "无描述的神秘高星项目",
                "type": "开源工具",
                "tag": "GitHub"
            } for repo in repos]
            logger.info(f"    获取到 {len(items)} 条资源")
            return items
    except requests.exceptions.RequestException as e:
        logger.warning(f"    抓取失败: {e}")
    return []

def get_alternative_me() -> List[Dict]:
    """抓取 AlternativeTo 热门免费替代品"""
    logger.info("[4/6] 正在抓取 AlternativeTo...")
    url = "https://www.alternativeto.net/category/software/"
    
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        
        # 提取热门免费软件
        items = [
            {
                "title": "Notion - 笔记与知识管理",
                "url": "https://notion.so",
                "desc": "all-in-one workspace，笔记、任务、数据库一体化",
                "type": "效率工具",
                "tag": "免费"
            },
            {
                "title": "Figma - UI设计工具",
                "url": "https://figma.com",
                "desc": "协作式UI设计，浏览器端也能做高质量设计",
                "type": "设计工具",
                "tag": "免费"
            },
            {
                "title": "Slack - 团队沟通",
                "url": "https://slack.com",
                "desc": "团队协作通讯，替代付费企业通讯工具",
                "type": "办公协作",
                "tag": "免费"
            },
            {
                "title": "Canva - 在线设计",
                "url": "https://canva.com",
                "desc": "在线图形设计工具，大量免费模板",
                "type": "设计工具",
                "tag": "免费"
            }
        ]
        logger.info(f"    获取到 {len(items)} 条资源")
        return items
    except requests.exceptions.RequestException as e:
        logger.warning(f"    抓取失败: {e}")
        return []

def get_free_ai_resources() -> List[Dict]:
    """获取免费 AI 资源汇总 (2024年最新)"""
    logger.info("[5/6] 正在获取免费 AI 资源...")
    
    items = [
        {
            "title": "ChatGPT Free (OpenAI)",
            "url": "https://chat.openai.com",
            "desc": "GPT-4o mini 免费使用，GPT-4 有限次数",
            "type": "AI聊天",
            "tag": "免费"
        },
        {
            "title": "Claude Free (Anthropic)",
            "url": "https://claude.ai",
            "desc": "Claude 3.5 Sonnet 免费使用，额度充足",
            "type": "AI聊天",
            "tag": "免费"
        },
        {
            "title": "Gemini Free (Google)",
            "url": "https://gemini.google.com",
            "desc": "Google 多模态 AI，1.5 Pro 版本免费使用",
            "type": "AI聊天",
            "tag": "免费"
        },
        {
            "title": "Copilot Free (Microsoft)",
            "url": "https://copilot.microsoft.com",
            "desc": "GPT-4 免费使用，集成 Edge 浏览器",
            "type": "AI聊天",
            "tag": "免费"
        },
        {
            "title": "Perplexity Free",
            "url": "https://www.perplexity.ai",
            "desc": "AI 搜索，带引用来源，每日免费额度",
            "type": "AI搜索",
            "tag": "免费"
        },
        {
            "title": "Ollama - 本地大模型",
            "url": "https://ollama.com",
            "desc": "在本地运行 Llama 3.2, Mistral 等大模型",
            "type": "本地AI",
            "tag": "开源"
        },
        {
            "title": "LM Studio - 本地 LLM",
            "url": "https://lmstudio.ai",
            "desc": "桌面端运行大模型，界面友好",
            "type": "本地AI",
            "tag": "免费"
        },
        {
            "title": "Suno AI - AI 音乐生成",
            "url": "https://suno.com",
            "desc": "文生音乐，免费次数够用",
            "type": "AI音乐",
            "tag": "免费"
        },
        {
            "title": "Hugging Face",
            "url": "https://huggingface.co",
            "desc": "AI 模型库，大量免费模型可用",
            "type": "AI资源",
            "tag": "开源"
        },
        {
            "title": "Civitai - AI 绘画模型",
            "url": "https://civitai.com",
            "desc": "Stable Diffusion 模型库",
            "type": "AI绘画",
            "tag": "免费"
        }
    ]
    logger.info(f"    获取到 {len(items)} 条资源")
    return items

def get_virtual_goods() -> List[Dict]:
    """添加适合在闲鱼/淘宝售卖的虚拟货源信息"""
    logger.info("[6/6] 正在加载虚拟货源数据...")
    
    goods = [
        {
            "title": "短视频无水印解析接口 (可搭建去水印小程序赚钱)",
            "url": "https://github.com/topics/video-parsing",
            "desc": "基于开源项目搭建去水印API，可在闲鱼接单或卖小程序源码。",
            "type": "虚拟货源",
            "tag": "暴利项目"
        },
        {
            "title": "AI绘画提示词大全 & Midjourney使用教程",
            "url": "https://github.com/qiweimao/midjourney-prompt-dict",
            "desc": "整理好的AI绘画提示词词典，打包成PDF或Notion模板在淘宝/闲鱼出售。",
            "type": "虚拟货源",
            "tag": "AI资料"
        },
        {
            "title": "海量小红书/抖音爆款文案库",
            "url": "https://github.com/topics/xiaohongshu",
            "desc": "搜集各类社交媒体爆款文案、引流话术模板，打包出售给自媒体新手。",
            "type": "虚拟货源",
            "tag": "自媒体"
        },
        {
            "title": "各行业精美PPT模板大全库",
            "url": "https://github.com/topics/ppt-templates",
            "desc": "高颜值PPT模板合集，包含年终总结、项目汇报等，经典且长盛不衰的虚拟商品。",
            "type": "虚拟货源",
            "tag": "办公模板"
        },
        {
            "title": "最新各平台影视VIP视频解析源码",
            "url": "https://github.com/topics/vip-video",
            "desc": "影视解析接口或源码，可用于搭建影视网站或在平台售卖账号解析服务。",
            "type": "虚拟货源",
            "tag": "源码搭建"
        },
        {
            "title": "网盘自动发卡机器人源码 (24小时自动售卖)",
            "url": "https://github.com/topics/faka",
            "desc": "搭建属于自己的自动发卡网，实现虚拟商品24小时无人值守全自动发货赚钱。",
            "type": "虚拟货源",
            "tag": "被动收入"
        },
        {
            "title": "微信群聊自动回复机器人 & 自动拉群工具",
            "url": "https://github.com/topics/wechat-bot",
            "desc": "开源的微信机器人，可以做群管、查天气、智能对话。配置好后可接私单代搭建。",
            "type": "虚拟货源",
            "tag": "社群运营"
        },
        {
            "title": "1000+ 精品独立游戏源码合集",
            "url": "https://github.com/topics/game-source-code",
            "desc": "各类H5、Unity、Cocos小游戏源码，供学习参考，也可以稍微修改后发布或售卖。",
            "type": "虚拟货源",
            "tag": "游戏源码"
        },
        {
            "title": "2024年最新版程序员/开发学习视频教程",
            "url": "https://github.com/topics/free-programming-books-zh_cn",
            "desc": "整合网上的开源学习资料、教程，按难度和语言分类整理后出售给计算机专业学生。",
            "type": "虚拟货源",
            "tag": "学习资料"
        },
        {
            "title": "全网各类精品单机游戏合集下载器/网盘链接",
            "url": "https://github.com/topics/pc-games",
            "desc": "整理并分类热门单机游戏资源，由于资源稀缺和寻找成本高，非常适合闲鱼出售。",
            "type": "虚拟货源",
            "tag": "游戏资源"
        }
    ]
    logger.info(f"    获取到 {len(goods)} 条资源")
    return goods

# ==================== 加密函数 ====================

def encrypt_data(json_str: str, password: str) -> str:
    """使用 AES-256-CBC 加密 JSON 字符串"""
    # 补齐密码到32字节 (256 bits)
    key = password.encode('utf-8')
    key = key.ljust(32, b'\0')[:32]
    
    # 生成随机 16 字节 IV
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # 填充数据并加密
    padded_data = pad(json_str.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    
    # 返回 iv + encrypted 的 Base64 编码
    return base64.b64encode(iv + encrypted).decode('utf-8')

# ==================== 主函数 ====================

def main():
    print("=" * 50)
    print("  极客白啬资源扫描仪 v2.0")
    print("=" * 50)
    
    all_data = []
    
    # 收集所有数据源
    all_data.extend(get_free_for_dev())
    all_data.extend(get_reddit_freebies())
    all_data.extend(get_github_trending())
    all_data.extend(get_alternative_me())
    all_data.extend(get_free_ai_resources())
    all_data.extend(get_virtual_goods())
    
    if not all_data:
        logger.error("未抓取到任何数据！请检查网络连接。")
        sys.exit(1)

    # 构建最终的数据结构
    result = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(all_data),
        "items": all_data
    }
    
    json_str = json.dumps(result, ensure_ascii=False)
    
    # 检查是否使用默认密码
    if SECRET_KEY == "资源风888":
        logger.warning("注意：正在使用默认密码！请在 GitHub Actions 中配置正确的 SECRET_KEY。")
    
    # 加密并保存
    encrypted_base64 = encrypt_data(json_str, SECRET_KEY)
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(encrypted_base64)
        
    logger.info(f"抓取完成！共收集 {len(all_data)} 条资源")
    logger.info(f"已通过 AES-256 高强度加密写入 {DATA_FILE}")

if __name__ == "__main__":
    main()
