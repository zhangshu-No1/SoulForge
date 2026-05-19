#!/usr/bin/env python3
"""
SoulForge 定时任务系统

不打造数字员工，只锻造数字灵魂。

这个脚本可以定期运行 SoulForge 相关任务，比如：
- 每日问候
- 记忆整理
- 目标进度检查
"""

import os
import sys
import time
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('soulforge_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SoulForgeScheduler')

# 尝试导入调度库
try:
    import schedule
except ImportError:
    logger.warning("schedule 库未安装，使用简单模式")
    schedule = None


class SoulForgeScheduler:
    """SoulForge 定时任务管理器"""
    
    def __init__(self, memory_dir='memory', name='慧慧'):
        self.memory_dir = memory_dir
        self.name = name
        self.sf = None
        self.last_memory_update = None
        
        # 确保记忆目录存在
        Path(memory_dir).mkdir(parents=True, exist_ok=True)
    
    def init_soulforge(self, adapter_type='deepseek', api_key=''):
        """初始化 SoulForge"""
        try:
            from soulforge import SoulForge
            self.sf = SoulForge(
                name=self.name,
                memory_dir=self.memory_dir,
                adapter_type=adapter_type,
                api_key=api_key
            )
            logger.info(f"✅ SoulForge 初始化成功！名字：{self.name}")
            return True
        except Exception as e:
            logger.error(f"❌ SoulForge 初始化失败：{e}")
            return False
    
    def task_daily_greeting(self):
        """每日问候任务"""
        logger.info("📅 执行每日问候任务...")
        
        now = datetime.now()
        hour = now.hour
        
        greetings = [
            f"早上好！又是新的一天，今天也要元气满满哦！☀️",
            f"晚上好！今天过得怎么样？来聊聊天吧！🌙",
            f"嗨！我想你了！最近在忙什么呢？💭",
            f"你好呀！有什么有趣的事情想和我分享吗？✨",
        ]
        
        # 根据时间选择问候语
        if 6 <= hour < 12:
            greeting = greetings[0]
        elif 18 <= hour < 24:
            greeting = greetings[1]
        else:
            greeting = random.choice(greetings[2:])
        
        # 保存到对话日志
        if self.sf:
            try:
                self.sf.memory.log_conversation(self.name, greeting)
                logger.info(f"💬 已发送问候：{greeting[:30]}...")
            except Exception as e:
                logger.error(f"❌ 发送问候失败：{e}")
        else:
            logger.info(f"💬 问候语：{greeting}")
        
        return greeting
    
    def task_memory_summary(self):
        """记忆整理任务"""
        logger.info("🧠 执行记忆整理任务...")
        
        if not self.sf:
            logger.warning("⚠️  SoulForge 未初始化，跳过记忆整理")
            return
        
        try:
            stats = self.sf.get_memory_stats()
            logger.info(f"📊 当前记忆统计：{stats['memory_index_entries']} 条记忆")
            
            # 可以在这里添加记忆自动整理逻辑
            # 比如给重要记忆添加标签等
            
            logger.info("✅ 记忆整理完成")
        except Exception as e:
            logger.error(f"❌ 记忆整理失败：{e}")
    
    def task_goal_check(self):
        """目标检查任务"""
        logger.info("🎯 执行目标检查任务...")
        
        if not self.sf:
            logger.warning("⚠️  SoulForge 未初始化，跳过目标检查")
            return
        
        try:
            goal_stats = self.sf.get_goal_stats()
            logger.info(f"📊 目标统计：{goal_stats}")
            logger.info("✅ 目标检查完成")
        except Exception as e:
            logger.error(f"❌ 目标检查失败：{e}")
    
    def task_heartbeat(self):
        """心跳任务（只是记录一下）"""
        logger.info("💓 SoulForge 定时任务系统运行中...")
    
    def run_once(self):
        """运行一次所有任务"""
        logger.info("=" * 60)
        logger.info("🚀 SoulForge 定时任务启动")
        logger.info(f"🕐 当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        self.task_heartbeat()
        self.task_daily_greeting()
        self.task_memory_summary()
        self.task_goal_check()
        
        logger.info("=" * 60)
        logger.info("✅ 所有任务执行完成！")
        logger.info("=" * 60)
    
    def run_schedule(self, interval_minutes=30):
        """持续运行定时任务"""
        if not schedule:
            logger.error("❌ schedule 库未安装！请运行：pip install schedule")
            return
        
        logger.info(f"⏰ 启动定时任务，每 {interval_minutes} 分钟执行一次")
        
        # 设置定时任务
        schedule.every(interval_minutes).minutes.do(self.run_once)
        schedule.every().day.at("09:00").do(self.task_daily_greeting)
        schedule.every().day.at("21:00").do(self.task_daily_greeting)
        
        logger.info("📋 已设置定时任务：")
        logger.info(f"  - 每 {interval_minutes} 分钟：完整检查")
        logger.info("  - 每天 09:00：早上好问候")
        logger.info("  - 每天 21:00：晚上好问候")
        logger.info("\n按 Ctrl+C 停止运行\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("\n👋 定时任务已停止")


def print_help():
    """显示帮助"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 SoulForge 定时任务系统                        ║
║            不打造数字员工，只锻造数字灵魂                       ║
╚══════════════════════════════════════════════════════════════╝

用法：
  python scheduler.py [选项]

选项：
  --once               运行一次所有任务（适合测试）
  --daemon             持续运行定时任务（默认每30分钟）
  --interval N         设置间隔为 N 分钟（仅 --daemon 模式）
  --memory-dir DIR     设置记忆目录（默认：memory）
  --name NAME          设置 AI 名字（默认：慧慧）
  --adapter TYPE       设置适配器类型（openai/claude/deepseek/doubao）
  --api-key KEY        设置 API 密钥
  --help               显示此帮助

示例：
  # 运行一次测试
  python scheduler.py --once
  
  # 持续运行，每60分钟检查一次
  python scheduler.py --daemon --interval 60
  
  # 使用 DeepSeek 运行
  python scheduler.py --once --adapter deepseek --api-key sk-xxx
""")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SoulForge 定时任务系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 运行一次测试
  python scheduler.py --once
  
  # 持续运行，每60分钟检查一次
  python scheduler.py --daemon --interval 60
  
  # 使用 DeepSeek 运行
  python scheduler.py --once --adapter deepseek --api-key sk-xxx
"""
    )
    
    parser.add_argument('--once', action='store_true', help='运行一次所有任务')
    parser.add_argument('--daemon', action='store_true', help='持续运行定时任务')
    parser.add_argument('--interval', type=int, default=30, help='定时任务间隔（分钟）')
    parser.add_argument('--memory-dir', default='memory', help='记忆目录')
    parser.add_argument('--name', default='慧慧', help='AI 名字')
    parser.add_argument('--adapter', default='deepseek', 
                        choices=['openai', 'claude', 'deepseek', 'doubao', 'local'],
                        help='适配器类型')
    parser.add_argument('--api-key', default='', help='API 密钥')
    
    args = parser.parse_args()
    
    if not args.once and not args.daemon:
        parser.print_help()
        print("\n提示：请使用 --once 或 --daemon 选项\n")
        return
    
    # 创建调度器
    scheduler = SoulForgeScheduler(
        memory_dir=args.memory_dir,
        name=args.name
    )
    
    # 尝试初始化 SoulForge（不需要 API Key 也能运行部分任务）
    if args.api_key:
        scheduler.init_soulforge(
            adapter_type=args.adapter,
            api_key=args.api_key
        )
    
    # 运行任务
    if args.once:
        scheduler.run_once()
    elif args.daemon:
        scheduler.run_schedule(interval_minutes=args.interval)


if __name__ == "__main__":
    main()
