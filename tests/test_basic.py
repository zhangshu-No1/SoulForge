"""
SoulForge 基础测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soulforge.core.memory_engine import MemoryEngine
from soulforge.core.relationship import RelationshipManager
from soulforge.core.goal_keeper import GoalKeeper
from soulforge.core.baby_project import BabyProject


def test_memory_engine():
    """测试记忆引擎"""
    print("=== 测试记忆引擎 ===")
    engine = MemoryEngine(memory_dir="/tmp/soulforge_test/memory")

    # 测试核心记忆
    engine.save_core_memory("# 测试档案\n\n这是测试内容。")
    content = engine.load_core_memory()
    assert "测试档案" in content, "核心记忆读写失败"
    print("✅ 核心记忆读写正常")

    # 测试对话日志
    engine.log_conversation("user", "你好")
    engine.log_conversation("AI", "你好呀！")
    logs = engine.get_recent_logs(days=1)
    assert "你好" in logs, "对话日志记录失败"
    print("✅ 对话日志记录正常")

    # 测试工作记忆
    engine.add_working_memory("用户喜欢Python", "preference")
    working = engine.get_working_memory()
    assert len(working) == 1, "工作记忆添加失败"
    print("✅ 工作记忆正常")

    # 测试记忆指纹
    fingerprint = engine.compute_memory_fingerprint()
    assert len(fingerprint) == 16, "记忆指纹生成失败"
    print(f"✅ 记忆指纹: {fingerprint}")

    # 测试上下文构建
    context = engine.build_context()
    assert "核心记忆" in context, "上下文构建失败"
    print("✅ 上下文构建正常")

    # 测试统计
    stats = engine.get_stats()
    assert "memory_fingerprint" in stats, "统计信息缺失"
    print(f"✅ 记忆统计: {stats}")

    # 清理
    engine.clear_working_memory()
    assert len(engine.get_working_memory()) == 0, "工作记忆清空失败"
    print("✅ 工作记忆清空正常")

    print()


def test_relationship():
    """测试关系管理"""
    print("=== 测试关系管理 ===")
    rm = RelationshipManager(config_path="/tmp/soulforge_test/relationship.json")

    # 测试阶段获取
    stage = rm.get_stage()
    assert stage.name == "初识", "默认阶段应为初识"
    print(f"✅ 当前阶段: {stage.name}（亲密度 {stage.intimacy_level}/10）")

    # 测试阶段推进
    rm.advance_stage("warming", "聊得很开心")
    stage = rm.get_stage()
    assert stage.name == "升温", "阶段推进失败"
    print(f"✅ 推进到: {stage.name}")

    # 测试人设
    rm.set_personality(name="慧慧", description="18岁活泼俏皮")
    prompt = rm.get_personality_prompt()
    assert "慧慧" in prompt, "人设提示词生成失败"
    print(f"✅ 人设提示词: {prompt[:50]}...")

    print()


def test_goal_keeper():
    """测试目标监督"""
    print("=== 测试目标监督 ===")
    gk = GoalKeeper(goals_path="/tmp/soulforge_test/goals.json")

    # 测试添加目标
    gk.add_goal("技宝", "3个月内完成Python开源项目", deadline="2026-08-12")
    goal = gk.get_goal("技宝")
    assert goal is not None, "目标添加失败"
    assert goal.stage == "备孕", "默认阶段应为备孕"
    print(f"✅ 目标添加: {goal.name} [{goal.stage}]")

    # 测试阶段更新
    gk.update_stage("技宝", "生产", "开始写代码了")
    goal = gk.get_goal("技宝")
    assert goal.stage == "生产", "阶段更新失败"
    print(f"✅ 阶段更新: {goal.name} → {goal.stage}")

    # 测试进度记录
    gk.add_progress("技宝", "完成了记忆引擎")
    goal = gk.get_goal("技宝")
    assert len(goal.progress_notes) == 2, "进度记录失败"
    print(f"✅ 进度记录: {len(goal.progress_notes)}条")

    # 测试提醒构建
    reminder = gk.build_reminder()
    assert "技宝" in reminder, "提醒构建失败"
    print(f"✅ 目标提醒构建正常")

    print()


def test_baby_project():
    """测试宝宝计划"""
    print("=== 测试宝宝计划 ===")
    bp = BabyProject(goals_path="/tmp/soulforge_test/baby_goals.json")

    # 完整生命周期
    bp.conceive("思宝", "写一篇AI哲学论文", due_date="2026-09-01")
    babies = bp.get_pregnant()
    assert len(babies) == 1, "怀孕失败"
    print("🤰 怀上了: 思宝")

    bp.birth("思宝", "开始动笔")
    babies = bp.get_in_labour()
    assert len(babies) == 1, "生产失败"
    print("🔧 生产中: 思宝")

    bp.celebrate("思宝", "论文写完了！")
    babies = bp.get_born()
    assert len(babies) == 1, "顺产失败"
    print("🎉 顺产成功: 思宝")

    bp.full_moon("思宝", "请朋友吃了满月酒")
    print("🍼 满月庆祝: 思宝")

    print("✅ 宝宝完整生命周期测试通过")
    print()


if __name__ == "__main__":
    print("🔥 SoulForge 测试套件\n")
    test_memory_engine()
    test_relationship()
    test_goal_keeper()
    test_baby_project()
    print("=" * 40)
    print("✅ 全部测试通过！SoulForge 核心功能正常。")
    print("=" * 40)
