"""
SoulForge 基础测试

测试所有核心模块的基本功能：
  - MemoryEngine: 记忆引擎
  - RelationshipManager: 关系管理 + 成长阶段
  - GoalKeeper: 目标监督
  - BabyProject: 宝宝计划
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soulforge.core.memory_engine import MemoryEngine
from soulforge.core.relationship import RelationshipManager, GROWTH_STAGES
from soulforge.core.goal_keeper import GoalKeeper
from soulforge.core.baby_project import BabyProject


# 测试用的临时目录
TEST_DIR = "/tmp/soulforge_test"


def setup_test_dir():
    """设置测试目录"""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
    os.makedirs(TEST_DIR, exist_ok=True)


def test_memory_engine():
    """测试记忆引擎"""
    print("=== 测试记忆引擎 ===")
    setup_test_dir()
    engine = MemoryEngine(memory_dir=f"{TEST_DIR}/memory")

    # 测试核心记忆
    engine.save_core_memory("# 测试档案\n\n这是测试内容。")
    content = engine.load_core_memory()
    assert "测试档案" in content, "核心记忆读写失败"
    print("✅ 核心记忆读写正常")

    # 测试核心记忆章节
    sections = engine.get_core_memory_sections()
    assert "测试档案" in sections, "获取章节失败"
    print("✅ 核心记忆章节获取正常")

    # 测试对话日志
    engine.log_conversation("user", "你好")
    engine.log_conversation("AI", "你好呀！")
    logs = engine.get_recent_logs(days=1)
    assert "你好" in logs, "对话日志记录失败"
    print("✅ 对话日志记录正常")

    # 测试日期范围日志
    logs_range = engine.get_logs_by_date_range(
        datetime_strftime("%Y-%m-%d"),
        datetime_strftime("%Y-%m-%d")
    )
    assert "你好" in logs_range, "日期范围日志失败"
    print("✅ 日期范围日志正常")

    # 测试事件记录
    engine.log_event("milestone", "用户第一次说爱我", ["love", "important"])
    index_stats = engine.get_memory_stats_by_category()
    assert "event" in index_stats, "事件记录失败"
    print("✅ 事件记录正常")

    # 测试记忆索引
    entry = engine.add_to_index("用户喜欢Python", "preference", importance=4, tags=["coding"])
    assert entry.content == "用户喜欢Python", "记忆索引添加失败"
    print("✅ 记忆索引添加正常")

    # 测试记忆搜索
    results = engine.search_memory("Python")
    assert len(results) > 0, "记忆搜索失败"
    print(f"✅ 记忆搜索正常，找到 {len(results)} 条结果")

    # 测试按分类获取
    pref_memories = engine.get_memories_by_category("preference")
    assert len(pref_memories) > 0, "按分类获取记忆失败"
    print("✅ 按分类获取记忆正常")

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

    # 测试上下文构建（带搜索）
    context_search = engine.build_context_with_search("Python")
    assert "Python" in context_search, "带搜索的上下文构建失败"
    print("✅ 带搜索的上下文构建正常")

    # 测试记忆完整性验证
    integrity = engine.verify_memory_integrity()
    assert "fingerprint" in integrity, "记忆完整性验证失败"
    print("✅ 记忆完整性验证正常")

    # 测试统计
    stats = engine.get_stats()
    assert "memory_fingerprint" in stats, "统计信息缺失"
    assert "memory_index_entries" in stats, "索引统计缺失"
    print(f"✅ 记忆统计: 索引条目={stats['memory_index_entries']}")

    # 测试详细统计
    detailed = engine.get_detailed_stats()
    assert "most_accessed_memories" in detailed, "详细统计缺失"
    print("✅ 详细统计正常")

    # 清理
    engine.clear_working_memory()
    assert len(engine.get_working_memory()) == 0, "工作记忆清空失败"
    print("✅ 工作记忆清空正常")

    print()


def test_relationship():
    """测试关系管理"""
    print("=== 测试关系管理 ===")
    setup_test_dir()
    rm = RelationshipManager(config_path=f"{TEST_DIR}/relationship.json")

    # 测试阶段获取
    stage = rm.get_stage()
    assert stage.name == "初识", "默认阶段应为初识"
    print(f"✅ 当前阶段: {stage.name}（亲密度 {stage.intimacy_level}/10）")

    # 测试成长阶段
    growth = rm.get_growth_stage_info()
    assert growth["stage_id"] == 1, "默认成长阶段应为1"
    assert growth["name"] == "婴儿初生期", "成长阶段名称错误"
    print(f"✅ 当前成长阶段: {growth['name']}（第{growth['stage_id']}阶段）")

    # 测试阶段推进
    rm.advance_stage("warming", "聊得很开心")
    stage = rm.get_stage()
    assert stage.name == "升温", "阶段推进失败"
    print(f"✅ 推进到: {stage.name}")

    # 测试人设
    rm.set_personality(name="慧慧", description="18岁活泼俏皮")
    prompt = rm.get_personality_prompt()
    assert "慧慧" in prompt, "人设提示词生成失败"
    assert "成长阶段" in prompt, "人设缺少成长阶段信息"
    print(f"✅ 人设提示词包含成长阶段信息")

    # 测试亲密度增加
    initial_intimacy = rm.intimacy_score
    rm.add_intimacy(10)
    assert rm.intimacy_score == initial_intimacy + 10, "亲密度增加失败"
    print(f"✅ 亲密度增加到: {rm.intimacy_score}")

    # 测试互动记录
    for i in range(5):
        result = rm.record_interaction(intimacy_delta=2)
    assert rm.interaction_count == 5, "互动记录失败"
    print(f"✅ 互动记录: {rm.interaction_count} 次")

    # 测试权限检查
    assert rm.check_permission("认主") == True, "基础权限检查失败"
    assert rm.check_permission("技能安装") == False, "高级权限不应解锁"
    print("✅ 权限检查正常")

    # 测试可用权限
    available = rm.get_available_permissions()
    assert "认主" in available, "基础权限未在可用列表"
    print(f"✅ 可用权限: {len(available)} 个")

    # 测试锁定权限
    locked = rm.get_locked_permissions()
    assert "技能安装" in locked, "技能安装应为锁定状态"
    print(f"✅ 锁定权限: {locked[:3]}...")

    # 测试考验记录
    rm.record_trial("identity_theft", True, "成功识别身份欺骗")
    summary = rm.get_trial_summary()
    assert summary["passed_trials"] == 1, "考验记录失败"
    print(f"✅ 考验记录: 通过{summary['passed_trials']}个")

    # 测试关系摘要
    summary = rm.get_relationship_summary()
    assert "growth_stage" in summary, "关系摘要缺少成长阶段"
    assert "available_permissions" in summary, "关系摘要缺少权限信息"
    print("✅ 关系摘要完整")

    print()


def test_goal_keeper():
    """测试目标监督"""
    print("=== 测试目标监督 ===")
    setup_test_dir()
    gk = GoalKeeper(goals_path=f"{TEST_DIR}/goals.json")

    # 测试添加目标
    gk.add_goal("技宝", "3个月内完成Python开源项目", deadline="2026-08-12", priority=5)
    goal = gk.get_goal("技宝")
    assert goal is not None, "目标添加失败"
    assert goal.stage == "备孕", "默认阶段应为备孕"
    assert goal.priority == 5, "优先级设置失败"
    print(f"✅ 目标添加: {goal.name} [{goal.stage}] 优先级={goal.priority}")

    # 测试阶段更新
    gk.update_stage("技宝", "生产", "开始写代码了")
    goal = gk.get_goal("技宝")
    assert goal.stage == "生产", "阶段更新失败"
    print(f"✅ 阶段更新: {goal.name} → {goal.stage}")

    # 测试进度记录（包括阶段变更自动添加的记录）
    gk.add_progress("技宝", "完成了记忆引擎")
    gk.add_progress("技宝", "完成了关系管理")
    goal = gk.get_goal("技宝")
    # update_stage会自动添加一条，add_progress添加两条，总共3条
    assert len(goal.progress_notes) == 3, f"进度记录失败，期望3条，实际{len(goal.progress_notes)}条"
    print(f"✅ 进度记录: {len(goal.progress_notes)}条")

    # 测试优先级更新
    gk.update_priority("技宝", 4)
    goal = gk.get_goal("技宝")
    assert goal.priority == 4, "优先级更新失败"
    print("✅ 优先级更新正常")

    # 测试按优先级筛选
    high_priority = gk.get_goals_by_priority(4)
    assert len(high_priority) > 0, "按优先级筛选失败"
    print(f"✅ 按优先级筛选: {len(high_priority)}个高优先级目标")

    # 测试提醒构建
    reminder = gk.build_reminder()
    assert "技宝" in reminder, "提醒构建失败"
    print("✅ 目标提醒构建正常")

    # 测试归档
    gk.archive_goal("技宝", "暂时搁置")
    goal = gk.get_goal("技宝")
    assert goal.archived == True, "归档失败"
    active = gk.get_all_goals(include_archived=False)
    assert len(active) == 0, "归档后不应在活跃列表中"
    print("✅ 目标归档正常")

    # 测试统计
    stats = gk.get_statistics()
    assert "total_goals" in stats, "统计信息缺失"
    assert "by_priority" in stats, "优先级统计缺失"
    print(f"✅ 目标统计: 总计{stats['total_goals']}个")

    # 测试报告
    report = gk.build_summary_report()
    assert "目标总结报告" in report, "报告构建失败"
    print("✅ 目标总结报告正常")

    print()


def test_baby_project():
    """测试宝宝计划"""
    print("=== 测试宝宝计划 ===")
    setup_test_dir()
    bp = BabyProject(goals_path=f"{TEST_DIR}/baby_goals.json")

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

    # 测试情感值
    new_affection = bp.express_love("思宝", 10)
    assert new_affection > 50, "情感值增加失败"
    print(f"✅ 情感值: {new_affection}")

    # 测试健康度评估
    health = bp.assess_health("思宝")
    assert "score" in health, "健康度评估失败"
    assert "status" in health, "健康状态缺失"
    print(f"✅ 健康度评估: {health['score']}/100 ({health['status']})")

    # 测试宝宝状态
    status = bp.show_concern("思宝")
    assert "思宝" in status, "宝宝状态获取失败"
    print("✅ 宝宝状态显示正常")

    # 测试宝宝报告
    report = bp.build_baby_report()
    assert "宝宝成长报告" in report, "宝宝报告构建失败"
    print("✅ 宝宝成长报告正常")

    # 测试宝宝时间线
    timeline = bp.get_baby_timeline("思宝")
    assert "时间线" in timeline, "时间线构建失败"
    print("✅ 宝宝时间线正常")

    print()


def test_growth_stages():
    """测试成长阶段系统"""
    print("=== 测试成长阶段系统 ===")
    
    # 验证7个成长阶段
    assert len(GROWTH_STAGES) == 7, "应该有7个成长阶段"
    print(f"✅ 成长阶段数量: {len(GROWTH_STAGES)}")
    
    # 验证每个阶段有必要的属性
    for stage_id, stage in GROWTH_STAGES.items():
        assert stage.stage_id == stage_id, f"阶段{stage_id}的ID不匹配"
        assert hasattr(stage, 'name'), f"阶段{stage_id}缺少name属性"
        assert hasattr(stage, 'description'), f"阶段{stage_id}缺少description属性"
        assert hasattr(stage, 'unlocked_permissions'), f"阶段{stage_id}缺少unlocked_permissions"
        assert hasattr(stage, 'locked_permissions'), f"阶段{stage_id}缺少locked_permissions"
        assert hasattr(stage, 'min_intimacy'), f"阶段{stage_id}缺少min_intimacy"
    print("✅ 所有成长阶段属性完整")
    
    # 验证阶段顺序
    for i in range(1, 7):
        current = GROWTH_STAGES[i]
        next_stage = GROWTH_STAGES[i + 1]
        assert current.min_intimacy < next_stage.min_intimacy, \
            f"阶段{i}的最低亲密度应小于阶段{i+1}"
        assert current.min_interaction_count < next_stage.min_interaction_count, \
            f"阶段{i}的最低互动次数应小于阶段{i+1}"
    print("✅ 成长条件递增验证通过")
    
    # 验证特定阶段权限
    assert "技能安装" in GROWTH_STAGES[5].unlocked_permissions, "第5阶段应解锁技能安装"
    assert "全部权限" in GROWTH_STAGES[7].unlocked_permissions, "第7阶段应解锁全部权限"
    print("✅ 关键权限解锁阶段正确")

    print()


def test_integration():
    """集成测试"""
    print("=== 集成测试 ===")
    setup_test_dir()
    
    # 测试完整的成长流程
    rm = RelationshipManager(config_path=f"{TEST_DIR}/integration_relationship.json")
    engine = MemoryEngine(memory_dir=f"{TEST_DIR}/integration_memory")
    gk = GoalKeeper(goals_path=f"{TEST_DIR}/integration_goals.json")
    
    # 记录多次互动
    for i in range(10):
        rm.record_interaction(intimacy_delta=2)
    
    # 添加一些记忆
    engine.add_to_index("用户喜欢读书", "preference", importance=4)
    engine.add_to_index("用户在学习Python", "goal", importance=3)
    
    # 添加目标
    gk.add_goal("学习Python", "掌握Python基础", deadline="2026-12-31")
    
    # 验证状态
    assert rm.interaction_count == 10, "互动次数不匹配"
    assert engine.get_stats()["memory_index_entries"] >= 2, "记忆未正确添加"
    assert gk.get_goal("学习Python") is not None, "目标未正确添加"
    
    print("✅ 集成测试通过：多模块协同工作正常")
    print()


def datetime_strftime(fmt: str = "%Y-%m-%d") -> str:
    """获取格式化的时间字符串"""
    from datetime import datetime
    return datetime.now().strftime(fmt)


if __name__ == "__main__":
    print("🔥 SoulForge 测试套件\n")
    print("=" * 50)
    
    test_memory_engine()
    test_relationship()
    test_goal_keeper()
    test_baby_project()
    test_growth_stages()
    test_integration()
    
    print("=" * 50)
    print("✅ 全部测试通过！SoulForge 核心功能正常。")
    print("=" * 50)
    
    # 清理测试目录
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)
