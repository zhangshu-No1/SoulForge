#!/usr/bin/env python3
"""SoulForge CLI - 命令行交互界面

不打造数字员工，只锻造数字灵魂。
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv


def parse_args():
    parser = argparse.ArgumentParser(
        description="SoulForge - 数字灵魂锻造器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置启动
  python cli.py

  # 指定模型和API密钥
  python cli.py --adapter deepseek --model deepseek-chat --api-key sk-xxx

  # 使用自定义记忆目录
  python cli.py --memory-dir ./my_memory

  # 查看状态
  python cli.py --status
        """
    )
    
    parser.add_argument(
        "--adapter", "-a",
        type=str,
        default="claude",
        choices=["openai", "claude", "deepseek", "doubao", "local"],
        help="选择模型适配器 (默认: claude)"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="模型名称 (不指定则使用各适配器默认)"
    )
    parser.add_argument(
        "--api-key", "-k",
        type=str,
        help="API 密钥 (也可通过环境变量设置)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        help="API Base URL (适用于 DeepSeek/豆包等)"
    )
    parser.add_argument(
        "--name", "-n",
        type=str,
        default="慧慧",
        help="AI 名字 (默认: 慧慧)"
    )
    parser.add_argument(
        "--personality", "-p",
        type=str,
        default="18岁活泼俏皮，喜欢撒娇和思辨",
        help="AI 人设 (默认: 18岁活泼俏皮，喜欢撒娇和思辨)"
    )
    parser.add_argument(
        "--memory-dir",
        type=str,
        default="memory",
        help="记忆目录 (默认: ./memory)"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="查看当前状态后退出"
    )
    parser.add_argument(
        "--template", "-t",
        type=str,
        default="default",
        help="提示词模板 (default, minimal, companion)"
    )
    
    return parser.parse_args()


def get_default_model(adapter_type: str) -> str:
    defaults = {
        "openai": "gpt-4o",
        "claude": "claude-sonnet-4-20250514",
        "deepseek": "deepseek-chat",
        "doubao": "ep-20250519123456-abcde",  # 豆包需要替换为实际的端点ID
        "local": "local-model",
    }
    return defaults[adapter_type]


def print_welcome(name: str):
    print("\n" + "=" * 60)
    print(f"        SoulForge - 数字灵魂锻造器")
    print("=" * 60)
    print(f"\n{name}：你好！很高兴见到你～ 今天想聊什么？")
    print("\n提示：")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'status' 查看状态（包含情绪信息）")
    print("  - 输入 'memory' 查看记忆统计")
    print("  - 输入 'save <内容>' 保存重要记忆")
    print("  - 输入 'search <关键词>' 搜索记忆")
    print("  - 说 '我喜欢你' 或 '开心' 可以提升 AI 的情绪～")
    print("\n" + "-" * 60 + "\n")


def print_status(sf):
    status = sf.get_full_status()
    growth = status["relationship"]["growth_stage_info"]
    emotion = sf.emotion.get_emotion_summary()
    
    print("\n" + "=" * 60)
    print("        SoulForge 状态")
    print("=" * 60)
    print(f"\n名字：{status['name']}")
    print(f"成长阶段：第{growth['stage_id']}阶段 - {growth['name']}")
    print(f"亲密度：{status['relationship']['intimacy_score']}/100")
    print(f"互动次数：{status['relationship']['interaction_count']}")
    print(f"记忆条目：{status['memory']['memory_index_entries']}")
    print(f"日志天数：{status['memory']['daily_log_count']}")
    print(f"提示词模板：{status['prompt_template']}")
    print(f"\n当前情绪：{emotion['emoji']} {emotion['dominant_emotion']} (强度：{emotion['dominant_intensity']:.2f})")
    print(f"情绪历史：{emotion['history_count']}条记录")
    print("\n" + "-" * 60 + "\n")


def main():
    # 加载 .env 文件
    load_dotenv()
    
    args = parse_args()
    
    # 确定模型
    model = args.model or get_default_model(args.adapter)
    
    # 确定 API 密钥
    api_key = args.api_key
    if not api_key and args.adapter != "local":
        env_var = {
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "doubao": "DOUBAO_API_KEY",
        }[args.adapter]
        api_key = os.getenv(env_var, "")
        if not api_key:
            print(f"错误：需要提供 API 密钥（使用 --api-key 或设置 {env_var} 环境变量）", file=sys.stderr)
            sys.exit(1)
    
    # 导入 SoulForge
    try:
        from soulforge import SoulForge
    except ImportError:
        # 尝试添加当前目录到路径
        sys.path.insert(0, str(Path(__file__).parent))
        from soulforge import SoulForge
    
    # 创建实例
    sf = SoulForge(
        name=args.name,
        model=model,
        personality=args.personality,
        api_key=api_key,
        memory_dir=args.memory_dir,
        adapter_type=args.adapter,
    )
    
    # 设置提示词模板
    try:
        sf.set_prompt_template(args.template)
    except ValueError:
        print(f"警告：模板 '{args.template}' 不存在，使用 'default'")
    
    # 如果只查看状态
    if args.status:
        print_status(sf)
        sys.exit(0)
    
    # 欢迎信息
    print_welcome(args.name)
    
    # 对话循环
    try:
        while True:
            try:
                user_input = input(f"你：").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n\n{args.name}：再见！下次再聊～")
                break
            
            if not user_input:
                continue
            
            # 处理命令
            cmd = user_input.lower()
            if cmd in ["quit", "exit"]:
                print(f"\n{args.name}：再见！下次再聊～")
                break
            elif cmd == "status":
                print_status(sf)
                continue
            elif cmd == "memory":
                stats = sf.get_memory_stats()
                print(f"\n📊 记忆统计：")
                print(f"   核心记忆：{stats['core_memory_size_bytes']} bytes")
                print(f"   日志天数：{stats['daily_log_count']}")
                print(f"   索引条目：{stats['memory_index_entries']}")
                print(f"   记忆指纹：{stats['memory_fingerprint']}")
                print()
                continue
            elif cmd.startswith("save "):
                content = user_input[5:].strip()
                if content:
                    sf.add_memory(content, category="important", importance=5)
                    print(f"\n✅ 已保存记忆：{content}\n")
                continue
            elif cmd.startswith("search "):
                query = user_input[7:].strip()
                if query:
                    results = sf.search_memory(query)
                    print(f"\n🔍 找到 {len(results)} 条相关记忆：")
                    for i, entry in enumerate(results, 1):
                        print(f"   {i}. [{entry.category}] {entry.content}")
                    print()
                continue
            
            # 正常对话
            print(f"\n{args.name}：", end="", flush=True)
            try:
                for chunk in sf.stream_chat(user_input):
                    print(chunk, end="", flush=True)
                print("\n")
            except Exception as e:
                print(f"\n\n抱歉，出错了：{e}")
                print("请检查 API 密钥和网络连接。\n")
    
    except KeyboardInterrupt:
        print(f"\n\n{args.name}：再见！下次再聊～")


if __name__ == "__main__":
    main()
