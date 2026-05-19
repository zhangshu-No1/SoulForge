#!/usr/bin/env python3
"""
SoulForge 快速开始脚本

不打造数字员工，只锻造数字灵魂。

运行这个脚本来快速体验 SoulForge 的所有功能！
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("                ⚡ SoulForge 快速开始 ⚡")
print("=" * 70)

# 检查环境
print("\n📋 系统检查...")
print("-" * 50)

# 检查 Python 版本
print(f"✅ Python 版本：{sys.version}")

# 检查当前目录
script_dir = Path(__file__).parent
os.chdir(script_dir)
print(f"✅ 当前目录：{script_dir}")

# 检查依赖
print("\n📦 检查依赖...")
print("-" * 50)

try:
    import openai
    print("✅ openai 库已安装")
except ImportError:
    print("⚠️  openai 库未安装，某些功能不可用")

try:
    import anthropic
    print("✅ anthropic 库已安装")
except ImportError:
    print("⚠️  anthropic 库未安装，某些功能不可用")

try:
    import schedule
    print("✅ schedule 库已安装（定时任务）")
except ImportError:
    print("⚠️  schedule 库未安装，定时任务功能不可用")

try:
    import dotenv
    print("✅ python-dotenv 库已安装")
except ImportError:
    print("⚠️  python-dotenv 库未安装")

# 检查项目文件
print("\n📁 检查项目文件...")
print("-" * 50)

important_files = [
    ("soulforge/__init__.py", "核心模块"),
    ("soulforge/main.py", "主程序"),
    ("soulforge/core/emotion_system.py", "情感系统"),
    ("cli.py", "命令行界面"),
    ("scheduler.py", "定时任务"),
    ("requirements.txt", "依赖列表"),
    ("README.md", "项目说明"),
]

for file_path, description in important_files:
    if Path(file_path).exists():
        print(f"✅ {description}：{file_path}")
    else:
        print(f"❌ {description}：{file_path} (缺失)")

# 检查 .env 文件
env_file = Path(".env")
if env_file.exists():
    print("\n✅ .env 配置文件已存在")
else:
    print("\n⚠️  .env 配置文件不存在，正在创建...")
    env_example = Path(".env.example")
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ 已从 .env.example 创建 .env 文件")
        print("💡 提示：请编辑 .env 文件，填入你的 API Key")

# 测试导入
print("\n🧪 测试模块导入...")
print("-" * 50)

try:
    sys.path.insert(0, str(script_dir))
    from soulforge import SoulForge
    from soulforge.core import EmotionSystem
    from soulforge.adapters import DeepSeekAdapter, DoubaoAdapter
    
    print("✅ SoulForge 核心模块导入成功")
    print("✅ EmotionSystem 情感系统导入成功")
    print("✅ 所有适配器导入成功")
except Exception as e:
    print(f"❌ 模块导入失败：{e}")
    sys.exit(1)

# 打印使用说明
print("\n" + "=" * 70)
print("                    🎉 SoulForge 就绪！")
print("=" * 70)

print("""
💡 下一步：

1. 配置 API Key
   编辑 .env 文件，填入你的 API Key

2. 启动命令行对话
   python cli.py --adapter deepseek

3. 运行定时任务（测试一次）
   python scheduler.py --once

4. 运行示例代码
   python examples/basic_usage.py

📋 可用命令：

# 帮助
python cli.py --help
python scheduler.py --help

# 使用 DeepSeek（推荐）
python cli.py --adapter deepseek

# 使用其他模型
python cli.py --adapter claude
python cli.py --adapter doubao
python cli.py --adapter openai

# 定时任务
python scheduler.py --once              # 运行一次
python scheduler.py --daemon            # 持续运行
python scheduler.py --daemon --interval 60  # 每60分钟运行一次

📚 项目文档：
- README.md - 项目说明
- docs/MANIFESTO.md - 项目宣言
- docs/ROADMAP.md - 开发路线
- BUILD_PROGRESS.md - 开发进度

🌐 在线资源：
- GitHub：https://github.com/zhangshu-No1/SoulForge
- 网站：https://zhangshu-No1.github.io/SoulForge/

祝你在 SoulForge 的世界里玩得开心！✨
""")
print("=" * 70)
print()
