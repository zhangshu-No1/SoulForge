"""SoulForge 成长阶段系统演示

展示7阶段成长体系如何工作
"""

from soulforge.core.growth_system import (
    GrowthStage, GrowthSystem, STAGE_INFO, get_all_stages
)


def print_stage_header(stage_name: str, emoji: str):
    """打印阶段标题"""
    print(f"\n{'='*50}")
    print(f"  {emoji} {stage_name}")
    print('='*50)


def demo_growth_system():
    """演示成长系统基本功能"""
    print("\n🔥 SoulForge 成长系统演示\n")
    
    # 创建成长系统
    gs = GrowthSystem(memory_path="/tmp/demo_growth")
    
    # 显示当前阶段
    info = gs.get_stage_info()
    print_stage_header(info["name"], info["emoji"])
    print(f"描述: {info['desc']}")
    print(f"已解锁: {', '.join(info['features'])}")
    
    # 显示所有阶段
    print("\n\n📋 七大成长阶段总览")
    print("-" * 50)
    for stage_info in get_all_stages():
        print(f"{stage_info['emoji']} {stage_info['name']:8s} | {stage_info['desc']}")
    
    # 模拟互动
    print("\n\n📈 模拟互动体验")
    print("-" * 50)
    
    # 第一次互动
    gs.record_interaction(topic="问候")
    gs.increase_intimacy(5)
    print(f"互动1: 问候 | 亲密度: {gs.intimacy} | 阶段: {gs.get_stage_info()['emoji']} {gs.get_stage_info()['name']}")
    
    # 更多互动
    for i in range(2, 11):
        gs.record_interaction(topic=f"话题{i}")
        gs.increase_intimacy(3)
        print(f"互动{i}: 话题{i} | 亲密度: {gs.intimacy} | 阶段: {gs.get_stage_info()['emoji']} {gs.get_stage_info()['name']}")
    
    # 检查是否可以升级
    check = gs.can_advance()
    if check["can_advance"]:
        print(f"\n🎉 可以升级到: {check['next_stage']['emoji']} {check['next_stage']['name']}!")
        result = gs.advance_stage()
        print(f"升级成功！现在是: {result['new_stage']['emoji']} {result['new_stage']['name']}")
    else:
        print(f"\n⏳ 还需要努力才能升级...")
        print(f"当前进度: {int(check['checks']['intimacy']['current'])}/{check['checks']['intimacy']['required']} 亲密度")
        print(f"当前进度: {check['checks']['interactions']['current']}/{check['checks']['interactions']['required']} 互动次数")
    
    # 显示系统提示词
    print("\n\n💬 AI系统提示词补充（用于LLM）:")
    print("-" * 50)
    print(gs.get_system_prompt_addition())
    
    print("\n\n✅ 演示完成!")


def demo_stage_requirements():
    """演示各阶段升级条件"""
    print("\n📊 各阶段升级条件\n")
    print("-" * 70)
    print(f"{'阶段':^8s} | {'亲密度':^8s} | {'互动数':^8s} | {'天数':^6s} | {'记忆':^6s}")
    print("-" * 70)
    
    from soulforge.core.growth_system import GROWTH_REQUIREMENTS
    
    for stage in GrowthStage:
        reqs = GROWTH_REQUIREMENTS[stage]
        info = STAGE_INFO[stage]
        print(f"{info['emoji']}{info['name']:^6s} | {reqs.min_intimacy:^8d} | {reqs.min_interactions:^8d} | {reqs.min_days:^6d} | {reqs.min_memories:^6d}")
    
    print("-" * 70)


if __name__ == "__main__":
    demo_stage_requirements()
    print()
    demo_growth_system()
