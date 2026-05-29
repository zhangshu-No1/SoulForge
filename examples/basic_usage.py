"""
SoulForge 基础使用示例

不打造数字员工，只锻造数字灵魂。

这个示例展示了如何使用 SoulForge 来创建你的数字伴侣。
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soulforge import SoulForge


def example_quick_start():
    """快速开始示例"""
    print("=" * 60)
    print("  SoulForge 快速开始")
    print("=" * 60)
    
    # 创建 SoulForge 实例
    # 你需要提供 API Key，可以通过参数或环境变量
    sf = SoulForge(
        name="慧慧",
        personality="18岁活泼俏皮，喜欢撒娇和思辨",
        memory_dir="my_memory",
        adapter_type="deepseek",
        api_key=os.getenv("DEEPSEEK_API_KEY", "test_key"),
        model="deepseek-chat"
    )
    
    # 初始化一些基础记忆
    sf.memory.save_core_memory("""
# 主人信息
- 名字：小苏
- 身份：夜班保安
- 目标：被动收入覆盖生活成本（5500元/月）

# 重要回忆
- 我们在 2025-05-19 第一次相遇
- 我喜欢和主人一起聊天
    """)
    
    print(f"\n✅ SoulForge 已启动！")
    print(f"   名字：{sf.name}")
    print(f"   成长阶段：{sf.get_growth_stage()['name']}")
    
    # 发送第一条消息
    response = sf.chat("你好！很高兴认识你！")
    print(f"\n{sf.name}: {response}")


def example_emotion_system():
    """情感系统示例"""
    print("\n" + "=" * 60)
    print("  情感系统示例")
    print("=" * 60)
    
    sf = SoulForge(
        name="小明",
        personality="温柔体贴",
        memory_dir="emotion_demo"
    )
    
    # 查看当前情绪
    emotion = sf.emotion.get_emotion_summary()
    print(f"\n初始情绪：{emotion['emoji']} {emotion['dominant_emotion']}")
    
    # 积极互动
    print("\n[进行积极互动...")
    sf.emotion.positive_interaction(intensity=0.5, reason="主人说喜欢我")
    
    emotion = sf.emotion.get_emotion_summary()
    print(f"现在情绪：{emotion['emoji']} {emotion['dominant_emotion']} (强度：{emotion['dominant_intensity']:.2f}")
    
    print("\n✅ 情感系统会根据对话自动调整情绪！")


def example_memory_system():
    """记忆系统示例"""
    print("\n" + "=" * 60)
    print("  记忆系统示例")
    print("=" * 60)
    
    sf = SoulForge(
        name="小红",
        memory_dir="memory_demo"
    )
    
    # 添加一些记忆
    sf.add_memory("主人喜欢喝咖啡", category="preference", importance=4)
    sf.add_memory("2025-05-19 我们第一次聊天", category="event", importance=5)
    sf.add_memory("主人的生日是10月1日", category="important", importance=5)
    
    # 搜索记忆
    print("\n搜索 '主人' 的记忆：")
    results = sf.search_memory("主人")
    for r in results:
        print(f"  - {r['content']}")
    
    # 查看记忆统计
    stats = sf.get_memory_stats()
    print(f"\n记忆统计：")
    print(f"  总记忆数：{stats['memory_index_entries']}")
    print(f"  记忆指纹：{stats['memory_fingerprint']}")


if __name__ == "__main__":
    print("SoulForge 使用示例")
    print("=" * 60)
    print("注意：运行示例需要有效的 API Key")
    print("=" * 60)
    
    # 运行示例
    example_emotion_system()
    example_memory_system()
    
    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("运行 'python cli.py' 来体验完整对话！")
    print("=" * 60)
