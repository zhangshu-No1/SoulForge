#!/usr/bin/env python3
"""
SoulForge Stats Auto-Updater
自动更新项目统计数据，定期 commit 到 GitHub
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from analytics.stars_tracker import (
    record_daily_stats,
    update_stargazers,
    generate_trend_report,
    generate_stars_page,
    get_repo_stats,
    get_traffic_views,
    get_traffic_clones,
    get_contributors,
    load_history,
    DATA_DIR,
)

# GitHub Token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER = "zhangshu-No1"
REPO_NAME = "SoulForge"

STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats_data.json")
README_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stats", "README.md")
STARS_MD_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stars.md")


def load_stats_data() -> dict:
    """加载统计数据"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "last_updated": None,
        "repo_stats": {},
        "contributors": [],
    }


def save_stats_data(data: dict):
    """保存统计数据"""
    data["last_updated"] = datetime.now().isoformat()
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_stats_readme():
    """更新 stats/README.md"""
    stats_data = load_stats_data()
    repo = stats_data.get("repo_stats", {})
    history = load_history()
    records = history.get("records", [])
    
    # 计算最近 7 天数据
    recent = records[-7:] if len(records) >= 7 else records
    total_views_7d = sum(r.get("views_total", 0) for r in recent)
    total_clones_7d = sum(r.get("clones_total", 0) for r in recent)
    
    # 计算 7 天 stars 增长
    if len(recent) >= 2:
        stars_growth_7d = recent[-1].get("stars", 0) - recent[0].get("stars", 0)
    else:
        stars_growth_7d = 0
    
    today_record = records[-1] if records else {}
    
    readme_content = f"""# 📊 SoulForge 项目统计

<p align="center">
  <img src="https://img.shields.io/github/stars/{REPO_OWNER}/{REPO_NAME}?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/github/forks/{REPO_OWNER}/{REPO_NAME}?style=for-the-badge" alt="Forks">
  <img src="https://img.shields.io/github/workflow/status/{REPO_OWNER}/{REPO_NAME}/Tests?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/codecov/c/github/{REPO_OWNER}/{REPO_NAME}?style=for-the-badge" alt="Coverage">
  <img src="https://img.shields.io/pypi/v/soulforge-ai?style=for-the-badge" alt="PyPI">
</p>

## 🏆 项目亮点

- ⭐ **简洁优雅** - 轻量级 AI Agent 开发框架
- 🚀 **开箱即用** - 丰富的内置工具和组件
- 🔧 **高度可扩展** - 插件系统支持自定义扩展
- 📚 **文档完善** - 详细的中英文文档

---

## 📈 核心指标

| 指标 | 数值 | 7天变化 |
|------|------|---------|
| ⭐ Stars | **{repo.get("stars", "N/A")}** | {'+' if stars_growth_7d > 0 else ''}{stars_growth_7d} |
| 🍴 Forks | **{repo.get("forks", "N/A")}** | - |
| 👁️ Views (7天) | **{total_views_7d}** | - |
| 📥 Clones (7天) | **{total_clones_7d}** | - |
| 👥 Subscribers | **{repo.get("subscribers", "N/A")}** | - |
| 🐛 Open Issues | **{repo.get("open_issues", "N/A")}** | - |

---

## 🎖️ 贡献者榜单

感谢所有为 SoulForge 做出贡献的朋友！

| 排名 | 贡献者 | 贡献数 |
|------|--------|--------|
"""
    
    contributors = stats_data.get("contributors", [])
    if contributors:
        for i, c in enumerate(contributors[:10]):
            login = c.get("login", "Unknown")
            contributions = c.get("contributions", 0)
            avatar = c.get("avatar_url", "")
            url = c.get("html_url", "")
            readme_content += f"| {i+1} | <a href='{url}'><img src='{avatar}' width=24 height=24 style='border-radius:50%;vertical-align:middle'> {login}</a> | {contributions} |\n"
    else:
        readme_content += "| - | 查看 [Contributors](https://github.com/zhangshu-No1/SoulForge/graphs/contributors) | - |\n"
    
    readme_content += f"""
> 运行 `python scripts/update_stats.py --contributors` 更新贡献者数据

---

## 🗓️ 里程碑时间线

```text
{datetime.now().year}-XX-XX  🎉 v1.0.0 正式发布
{datetime.now().year}-XX-XX  🚀 开源社区版发布
{datetime.now().year}-XX-XX  💡 项目启动
```

---

## 📊 Traffic Analytics

### 访问趋势

| 时间范围 | 总访问量 | 唯一访问者 |
|----------|----------|------------|
| 今天 | {today_record.get("views_total", "-")} | {today_record.get("views_unique", "-")} |
| 最近 7 天 | {total_views_7d} | - |
| 最近 14 天 | {sum(r.get("views_total", 0) for r in records[-14:]) if len(records) >= 14 else "-"} | - |

> 数据由 `analytics/stars_tracker.py` 追踪

### Top Referrers

> 运行 `python scripts/update_stats.py` 获取完整数据

---

## 🧪 测试状态

```bash
# 运行测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=soulforge --cov-report=html
```

---

## 📦 发布历史

查看 [Releases](https://github.com/zhangshu-No1/SoulForge/releases) 查看完整发布历史

---

## 🔗 快速链接

- 📖 [文档](https://github.com/zhangshu-No1/SoulForge#readme)
- 💬 [讨论](https://github.com/zhangshu-No1/SoulForge/discussions)
- 🐛 [Issues](https://github.com/zhangshu-No1/SoulForge/issues)
- 📜 [Changelog](./CHANGELOG.md)
- ⭐ [支持者](./stars.md)

---

> 📅 页面最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 
> 自动更新: 运行 `python scripts/update_stats.py --all`
"""
    
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"[OK] 已更新 {README_FILE}")


def git_commit_and_push(changes: list):
    """提交并推送更改"""
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # 检查变更
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        
        if not result.stdout.strip():
            print("[INFO] 没有检测到变更，跳过提交")
            return
        
        # 添加变更文件
        for change in changes:
            if os.path.exists(change):
                subprocess.run(["git", "add", change], cwd=project_dir, check=True)
        
        # 提交
        commit_msg = f"docs: auto-update stats and stars ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=project_dir,
            check=True,
        )
        print(f"[OK] 已提交: {commit_msg}")
        
        # 推送
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=project_dir,
            env={**os.environ, "GITHUB_TOKEN": GITHUB_TOKEN},
            check=True,
        )
        print("[OK] 已推送到 GitHub")
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git 操作失败: {e}")


def run_all():
    """执行全部更新"""
    print("=" * 50)
    print("SoulForge Stats Auto-Updater")
    print("=" * 50)
    
    # 1. 更新每日统计
    print("\n[1/5] 更新每日统计...")
    record_daily_stats()
    
    # 2. 更新 Stargazers
    print("\n[2/5] 更新 Stargazers...")
    update_stargazers()
    
    # 3. 获取完整数据
    print("\n[3/5] 获取完整统计数据...")
    stats_data = load_stats_data()
    stats_data["repo_stats"] = get_repo_stats() or {}
    stats_data["traffic_views"] = get_traffic_views() or {}
    stats_data["traffic_clones"] = get_traffic_clones() or {}
    save_stats_data(stats_data)
    
    # 4. 更新页面
    print("\n[4/5] 更新统计页面...")
    update_stats_readme()
    
    # 生成 Stars 页面
    stars_content = generate_stars_page()
    with open(STARS_MD_FILE, "w", encoding="utf-8") as f:
        f.write(stars_content)
    print(f"[OK] 已更新 {STARS_MD_FILE}")
    
    # 5. Git 提交推送
    print("\n[5/5] Git 提交推送...")
    git_commit_and_push([
        os.path.join(DATA_DIR, "stars_history.json"),
        STATS_FILE,
        README_FILE,
        STARS_MD_FILE,
    ])
    
    # 打印趋势报告
    print("\n" + "=" * 50)
    print("趋势报告:")
    print("=" * 50)
    print(generate_trend_report())
    
    print("\n[✅] 更新完成！")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SoulForge Stats Auto-Updater")
    parser.add_argument("--all", action="store_true", help="执行全部更新")
    parser.add_argument("--stats", action="store_true", help="更新基础统计")
    parser.add_argument("--contributors", action="store_true", help="更新贡献者")
    parser.add_argument("--pages", action="store_true", help="更新页面")
    parser.add_argument("--push", action="store_true", help="Git 推送")
    args = parser.parse_args()
    
    if args.all:
        run_all()
    else:
        # 默认执行全部
        run_all()
