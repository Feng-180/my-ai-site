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

def main():
    print("========== 极客白嫖资源扫描仪 v1.0 ==========")
    all_data = []
    
    all_data.extend(get_free_for_dev())
    all_data.extend(get_reddit_freebies())
    all_data.extend(get_github_trending())
    
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
