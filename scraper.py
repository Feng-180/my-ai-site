import requests
import json
import re
import os
import base64
import time
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# --- 配置区 ---
DATA_FILE = "data.enc"  # 加密输出文件
SECRET_KEY = os.getenv("SECRET_KEY", "资源风888")  # 从环境变量获取密码（GitHub Actions中设置）

def get_free_for_dev():
    """抓取 free-for-dev 开发者白嫖资源 (只截取部分精华)"""
    print("[1] 正在抓取 Free-for-Dev...")
    url = "https://raw.githubusercontent.com/ripienaar/free-for-dev/master/README.md"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        text = resp.text
        
        # 简单正则匹配分类和链接 (提取最新或热门的一些)
        items = []
        # 匹配 `* [Name](url) - description`
        pattern = re.compile(r'^\* \[(.+?)\]\((.+?)\)(.*)$', re.MULTILINE)
        matches = pattern.findall(text)
        
        # 为了不撑爆页面，我们随机挑选或按序挑选30个
        for m in matches[:30]:
            name, link, desc = m
            desc = desc.strip(" -")
            if not desc: desc = "提供免费计划或额度的开发者服务"
            items.append({"title": name, "url": link, "desc": desc, "type": "云服务/API", "tag": "FreeTier"})
        return items
    except Exception as e:
        print(f"    抓取失败: {e}")
        return []

def get_reddit_freebies():
    """抓取 Reddit 限免板块的热门羊毛"""
    print("[2] 正在抓取 Reddit (eFreebies/Freebies)...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FreebiesScraper/1.0"}
    urls = [
        "https://www.reddit.com/r/eFreebies/hot.json?limit=15",
        "https://www.reddit.com/r/freebies/hot.json?limit=15"
    ]
    items = []
    for u in urls:
        try:
            resp = requests.get(u, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for child in data.get('data', {}).get('children', []):
                    post = child['data']
                    if not post.get('stickied') and not post.get('is_video'):
                        items.append({
                            "title": post['title'][:80] + "..." if len(post['title']) > 80 else post['title'],
                            "url": post['url'],
                            "desc": f"评分: {post['score']} | Reddit热门免费资源",
                            "type": "羊毛福利",
                            "tag": "限时免费"
                        })
        except Exception as e:
            print(f"    抓取 {u} 失败: {e}")
    return items

def get_github_trending():
    """抓取 GitHub 今日热门开源项目 (潜在的免费好工具)"""
    print("[3] 正在抓取 GitHub Trending...")
    url = "https://api.github.com/search/repositories?q=created:>2024-01-01&sort=stars&order=desc"
    try:
        # 只是简单获取最近高星项目作为平替工具的发现渠道
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            repos = resp.json().get("items", [])[:15]
            return [{
                "title": repo["full_name"],
                "url": repo["html_url"],
                "desc": repo["description"] or "无描述的神秘高星项目",
                "type": "开源工具",
                "tag": "GitHub"
            } for repo in repos]
    except Exception as e:
        print(f"    抓取失败: {e}")
    return []

def encrypt_data(json_str, password):
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


def get_virtual_goods():
    """添加适合在闲鱼/淘宝售卖的虚拟货源信息 (人工整理的精选源)"""
    print("[4] 正在加载虚拟货源数据...")
    
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
    return goods

def main():
    print("========== 极客白嫖资源扫描仪 v1.0 ==========")
    all_data = []
    
    all_data.extend(get_free_for_dev())
    all_data.extend(get_reddit_freebies())
    all_data.extend(get_github_trending())
    all_data.extend(get_virtual_goods())
    
    if not all_data:
        print("警告: 未抓取到任何数据！")
        return

    # 构建最终的数据结构
    result = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(all_data),
        "items": all_data
    }
    
    json_str = json.dumps(result, ensure_ascii=False)
    
    if SECRET_KEY == "你的默认测试密码":
        print("注意：正在使用默认测试密码！请在 GitHub Actions 中配置正确的 SECRET_KEY。")
        
    encrypted_base64 = encrypt_data(json_str, SECRET_KEY)
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(encrypted_base64)
        
    print(f"抓取完成！共收集 {len(all_data)} 条资源，已通过 AES-256 高强度加密写入 {DATA_FILE}")

if __name__ == "__main__":
    main()
