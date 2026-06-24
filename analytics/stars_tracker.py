#!/usr/bin/env python3
"""
SoulForge GitHub Stars Tracker
追踪 GitHub Stars、Forks、Views 变化，生成趋势报告
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# ============== 配置 ==============
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER = "zhangshu-No1"
REPO_NAME = "SoulForge"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
STARS_FILE = os.path.join(DATA_DIR, "stars_history.json")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "SoulForge-Stats-Bot"
}


# ============== GitHub API ==============
def api_get(url: str) -> Optional[dict]:
    """发送 GET 请求到 GitHub API"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[ERROR] API 请求失败: {e}")
        return None


def get_repo_stats() -> Optional[Dict]:
    """获取仓库基础统计"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    data = api_get(url)
    if not data:
        return None
    return {
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "subscribers": data.get("subscribers_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "language": data.get("language", "Unknown"),
        "description": data.get("description", ""),
    }


def get_traffic_views() -> Optional[Dict]:
    """获取流量视图数据"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/traffic/views"
    return api_get(url)


def get_traffic_clones() -> Optional[Dict]:
    """获取克隆数据"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/traffic/clones"
    return api_get(url)


def get_stargazers() -> List[Dict]:
    """获取所有 Stargazers（支持分页）"""
    stargazers = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/stargazers?per_page=100&page={page}"
        data = api_get(url)
        if not data or not isinstance(data, list):
            break
        stargazers.extend(data)
        if len(data) < 100:
            break
        page += 1
    return stargazers


def get_recent_commits(days: int = 30) -> List[Dict]:
    """获取最近提交"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?per_page=100"
    data = api_get(url)
    if not data:
        return []
    commits = []
    cutoff = datetime.now() - timedelta(days=days)
    for c in data:
        date_str = c.get("commit", {}).get("author", {}).get("date", "")
        if date_str:
            commit_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if commit_date.replace(tzinfo=None) < cutoff:
                break
            commits.append({
                "sha": c.get("sha", "")[:7],
                "message": c.get("commit", {}).get("message", "").split("\n")[0],
                "author": c.get("commit", {}).get("author", {}).get("name", ""),
                "date": date_str,
                "url": c.get("html_url", "")
            })
    return commits


def get_contributors() -> List[Dict]:
    """获取贡献者列表"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contributors?per_page=20"
    data = api_get(url)
    return data if isinstance(data, list) else []


# ============== 数据存储 ==============
def load_history() -> Dict:
    """加载历史数据"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(STARS_FILE):
        with open(STARS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"records": [], "stargazers": []}


def save_history(history: Dict):
    """保存历史数据"""
    with open(STARS_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def record_daily_stats():
    """记录每日统计数据"""
    history = load_history()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 检查是否已记录今天
    if history["records"] and history["records"][-1].get("date") == today:
        print(f"[INFO] 今天 ({today}) 已记录，跳过")
        return
    
    stats = get_repo_stats()
    if not stats:
        print("[ERROR] 无法获取仓库统计")
        return
    
    traffic_views = get_traffic_views() or {}
    traffic_clones = get_traffic_clones() or {}
    
    record = {
        "date": today,
        "stars": stats["stars"],
        "forks": stats["forks"],
        "subscribers": stats["subscribers"],
        "open_issues": stats["open_issues"],
        "views_total": traffic_views.get("count", 0),
        "views_unique": traffic_views.get("uniques", 0),
        "clones_total": traffic_clones.get("count", 0),
        "clones_unique": traffic_clones.get("uniques", 0),
    }
    
    history["records"].append(record)
    save_history(history)
    print(f"[OK] 记录 {today}: stars={stats['stars']}, forks={stats['forks']}")


def update_stargazers():
    """更新 Stargazers 列表"""
    history = load_history()
    print("[INFO] 获取 Stargazers 列表...")
    stargazers = get_stargazers()
    
    if stargazers:
        history["stargazers"] = stargazers
        save_history(history)
        print(f"[OK] 已记录 {len(stargazers)} 位 Stargazers")
    return stargazers


# ============== 报告生成 ==============
def generate_trend_report() -> str:
    """生成趋势报告"""
    history = load_history()
    records = history.get("records", [])
    
    if len(records) < 2:
        return "数据不足，需要至少 2 天数据才能生成趋势报告"
    
    recent = records[-7:]  # 最近 7 天
    oldest = records[0]
    newest = records[-1]
    
    stars_diff = newest.get("stars", 0) - oldest.get("stars", 0)
    forks_diff = newest.get("forks", 0) - oldest.get("forks", 0)
    
    days = len(recent)
    avg_views = sum(r.get("views_total", 0) for r in recent) / days if days else 0
    
    # 计算 7 日增长
    week_stars = sum(recent[i].get("stars", 0) - recent[i-1].get("stars", 0) 
                     for i in range(1, len(recent)))
    
    report = f"""
## 📊 SoulForge 趋势报告

### 整体统计
- ⭐ Stars: **{newest.get('stars', 0)}** ({stars_diff:+d} 总增长)
- 🍴 Forks: **{newest.get('forks', 0)}** ({forks_diff:+d} 总增长)
- 👥 Subscribers: **{newest.get('subscribers', 0)}**
- 🐛 Open Issues: **{newest.get('open_issues', 0)}**

### 近 7 天趋势
| 日期 | Stars | Forks | Views | Clones |
|------|-------|-------|-------|--------|
"""
    for r in recent:
        report += f"| {r['date']} | {r.get('stars', 0)} | {r.get('forks', 0)} | {r.get('views_total', 0)} | {r.get('clones_total', 0)} |\n"
    
    report += f"""
### 关键指标
- 📈 近 7 天新增 Stars: **{week_stars}**
- 👁️ 平均日 Views: **{avg_views:.0f}**
- 🔥 今日 Views: **{newest.get('views_total', 0)}** (唯一: {newest.get('views_unique', 0)})
- 📥 今日 Clones: **{newest.get('clones_total', 0)}** (唯一: {newest.get('clones_unique', 0)})

> 📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return report


def generate_stars_page() -> str:
    """生成 Stars 感谢页面"""
    history = load_history()
    stargazers = history.get("stargazers", [])
    
    page = """# ⭐ SoulForge Stars

<p align="center">
  <img src="https://img.shields.io/github/stars/zhangshu-No1/SoulForge?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/github/forks/zhangshu-No1/SoulForge?style=for-the-badge" alt="Forks">
</p>

感谢每一位支持 SoulForge 的朋友！🌟

"""
    
    if not stargazers:
        page += "> 暂无 Stars 数据，运行 `python analytics/stars_tracker.py --update` 获取\n"
        return page
    
    page += f"**感谢 {len(stargazers)} 位 Stargazer 的支持！**\n\n"
    
    # 按时间分组（最近活跃的在前）
    page += "## 🌟 全体支持者\n\n"
    
    for i, sg in enumerate(stargazers):
        login = sg.get("login", "Unknown")
        avatar = sg.get("avatar_url", "")
        profile_url = sg.get("html_url", "")
        
        page += f"""<a href="{profile_url}" target="_blank">
  <img src="{avatar}" width="60" height="60" style="border-radius:50%;margin:4px;" title="@{login}" alt="@{login}">
</a> """
        
        if (i + 1) % 10 == 0:
            page += "\n\n"
    
    page += "\n\n---\n*⭐ 感谢每一个 Star，让开源世界更美好*\n"
    return page


# ============== 主程序 ==============
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SoulForge Stars Tracker")
    parser.add_argument("--update", action="store_true", help="更新每日统计数据")
    parser.add_argument("--stargazers", action="store_true", help="更新 Stargazers 列表")
    parser.add_argument("--report", action="store_true", help="生成趋势报告")
    parser.add_argument("--all", action="store_true", help="执行全部操作")
    args = parser.parse_args()
    
    if args.all or args.update:
        record_daily_stats()
    
    if args.all or args.stargazers:
        update_stargazers()
    
    if args.all or args.report:
        print(generate_trend_report())
    
    if not any([args.update, args.stargazers, args.report, args.all]):
        # 默认显示趋势报告
        record_daily_stats()
        print(generate_trend_report())
