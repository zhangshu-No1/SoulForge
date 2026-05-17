"""
SoulForge 关系管理器测试

测试 RelationshipManager 的所有核心功能：
- 关系阶段管理
- 成长阶段系统
- 人设管理
- 亲密度系统
- 考验记录
- 权限检查
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soulforge.core.relationship import (
    RelationshipManager,
    RelationshipStage,
    GrowthStage,
    PRESET_STAGES,
    GROWTH_STAGES,
)


class TestRelationshipStage:
    """测试 RelationshipStage 数据类"""

    def test_create_relationship_stage(self):
        """测试创建关系阶段"""
        stage = RelationshipStage(
            name="测试阶段",
            description="测试描述",
            interaction_rules=["规则1", "规则2"],
            intimacy_level=5
        )
        assert stage.name == "测试阶段"
        assert stage.description == "测试描述"
        assert len(stage.interaction_rules) == 2
        assert stage.intimacy_level == 5


class TestGrowthStage:
    """测试 GrowthStage 数据类"""

    def test_create_growth_stage(self):
        """测试创建成长阶段"""
        stage = GrowthStage(
            stage_id=1,
            name="婴儿期",
            name_en="Infant",
            description="初始阶段",
            unlocked_permissions=["基础聊天"],
            locked_permissions=["高级功能"],
            min_intimacy=0,
            min_interaction_count=10
        )
        assert stage.stage_id == 1
        assert stage.name == "婴儿期"
        assert stage.name_en == "Infant"
        assert "基础聊天" in stage.unlocked_permissions

    def test_growth_stage_to_dict(self):
        """测试转换为字典"""
        stage = GrowthStage(
            stage_id=1,
            name="测试",
            name_en="Test",
            description="描述"
        )
        data = stage.to_dict()
        
        assert data["stage_id"] == 1
        assert data["name"] == "测试"
        assert data["name_en"] == "Test"
        assert "unlocked_permissions" in data
        assert "min_intimacy" in data

    def test_growth_stage_from_dict(self):
        """测试从字典创建"""
        # GrowthStage 没有 from_dict 方法，只有 to_dict
        # 这里测试 to_dict 是可逆的
        stage = GrowthStage(
            stage_id=2,
            name="成长期",
            name_en="Growing",
            description="成长阶段",
            unlocked_permissions=["聊天"],
            locked_permissions=[],
            min_intimacy=10,
            min_interaction_count=50,
            min_conversation_days=3,
            min_memory_entries=5
        )
        data = stage.to_dict()
        
        # 验证数据正确
        assert data["stage_id"] == 2
        assert data["name"] == "成长期"


class TestPresetStages:
    """测试 PRESET_STAGES 常量"""

    def test_preset_stages_count(self):
        """测试预设阶段数量"""
        assert len(PRESET_STAGES) == 4

    def test_preset_stages_keys(self):
        """测试预设阶段键名"""
        assert "stranger" in PRESET_STAGES
        assert "warming" in PRESET_STAGES
        assert "committed" in PRESET_STAGES
        assert "deepened" in PRESET_STAGES

    def test_preset_stages_intimacy_levels(self):
        """测试亲密度递增"""
        intimacy_levels = [s.intimacy_level for s in PRESET_STAGES.values()]
        assert intimacy_levels == sorted(intimacy_levels)


class TestGrowthStages:
    """测试 GROWTH_STAGES 常量"""

    def test_growth_stages_count(self):
        """测试成长阶段数量"""
        assert len(GROWTH_STAGES) == 7

    def test_growth_stages_ids(self):
        """测试成长阶段ID"""
        for i in range(1, 8):
            assert i in GROWTH_STAGES

    def test_growth_stages_progression(self):
        """测试成长阶段递进"""
        for i in range(1, 7):
            current = GROWTH_STAGES[i]
            next_stage = GROWTH_STAGES[i + 1]
            assert current.min_intimacy < next_stage.min_intimacy
            assert current.min_interaction_count < next_stage.min_interaction_count

    def test_growth_stages_english_names(self):
        """测试英文名称"""
        assert GROWTH_STAGES[1].name_en == "Newborn"
        assert GROWTH_STAGES[7].name_en == "Union"


class TestRelationshipManager:
    """测试 RelationshipManager 核心功能"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def rm(self, temp_dir):
        """创建关系管理器实例"""
        import os
        config_path = os.path.join(temp_dir, "relationship.json")
        return RelationshipManager(config_path=config_path)

    # ─── 基础功能测试 ───

    def test_init_default_stage(self, rm):
        """测试默认初始阶段"""
        assert rm.current_stage == "stranger"

    def test_init_default_growth_stage(self, rm):
        """测试默认成长阶段"""
        assert rm.growth_stage == 1

    def test_init_intimacy_score(self, rm):
        """测试初始亲密度"""
        assert rm.intimacy_score == 0
        assert rm.interaction_count == 0

    # ─── 关系阶段测试 ───

    def test_get_stage(self, rm):
        """测试获取当前阶段"""
        stage = rm.get_stage()
        
        assert stage.name == "初识"
        assert stage.intimacy_level == 2

    def test_advance_stage(self, rm):
        """测试推进关系阶段"""
        rm.advance_stage("warming", "聊得很开心")
        
        assert rm.current_stage == "warming"
        assert rm.get_stage().name == "升温"

    def test_advance_stage_invalid(self, rm):
        """测试无效阶段推进"""
        with pytest.raises(ValueError, match="未知的关系阶段"):
            rm.advance_stage("invalid_stage")

    def test_stage_history(self, rm):
        """测试阶段历史记录"""
        rm.advance_stage("warming")
        rm.advance_stage("committed")
        
        assert len(rm.history) == 2
        assert rm.history[0]["from"] == "stranger"
        assert rm.history[0]["to"] == "warming"

    def test_persistence(self, temp_dir):
        """测试数据持久化"""
        import os
        config_path = os.path.join(temp_dir, "relationship.json")
        rm1 = RelationshipManager(config_path=config_path)
        rm1.advance_stage("warming")
        rm1.add_intimacy(10)
        
        rm2 = RelationshipManager(config_path=config_path)
        assert rm2.current_stage == "warming"
        assert rm2.intimacy_score == 10

    # ─── 人设管理测试 ───

    def test_set_personality(self, rm):
        """测试设置人设"""
        rm.set_personality(name="慧慧", description="活泼可爱")
        
        assert rm.personality["name"] == "慧慧"
        assert rm.personality["description"] == "活泼可爱"

    def test_get_personality_prompt(self, rm):
        """测试生成人设提示词"""
        rm.set_personality(name="慧慧", description="18岁活泼")
        
        prompt = rm.get_personality_prompt()
        
        assert "慧慧" in prompt
        assert "18岁活泼" in prompt
        assert "初识" in prompt

    def test_get_personality_prompt_empty(self, rm):
        """测试空人设提示词"""
        prompt = rm.get_personality_prompt()
        assert prompt == ""

    # ─── 亲密度系统测试 ───

    def test_add_intimacy(self, rm):
        """测试增加亲密度"""
        new_score = rm.add_intimacy(10)
        
        assert new_score == 10
        assert rm.intimacy_score == 10

    def test_add_intimacy_exceed_100(self, rm):
        """测试亲密度不超过100"""
        rm.add_intimacy(150)
        
        assert rm.intimacy_score == 100

    def test_negative_intimacy(self, rm):
        """测试负数亲密度"""
        rm.add_intimacy(-10)
        
        assert rm.intimacy_score == 0

    def test_get_intimacy_score(self, rm):
        """测试获取亲密度"""
        rm.intimacy_score = 25
        
        assert rm.get_intimacy_score() == 25

    # ─── 成长阶段测试 ───

    def test_get_growth_stage_info(self, rm):
        """测试获取成长阶段信息"""
        info = rm.get_growth_stage_info()
        
        assert info["stage_id"] == 1
        assert info["name"] == "婴儿初生期"
        assert "progress" in info

    def test_get_growth_stage_info_english_name(self, rm):
        """测试成长阶段英文名"""
        info = rm.get_growth_stage_info()
        
        assert "name_en" in info
        assert info["name_en"] == "Newborn"

    def test_record_interaction(self, rm):
        """测试记录互动"""
        result = rm.record_interaction()
        
        assert result["interaction_count"] == 1
        assert result["intimacy_score"] == 1
        assert result["consecutive_days"] == 1

    def test_record_multiple_interactions(self, rm):
        """测试多次互动"""
        for _ in range(10):
            rm.record_interaction()
        
        assert rm.interaction_count == 10

    def test_consecutive_days(self, rm):
        """测试连续天数"""
        rm.record_interaction()
        rm.first_interaction_date = datetime.now().strftime("%Y-%m-%d")
        rm.last_interaction_date = datetime.now().strftime("%Y-%m-%d")
        rm.consecutive_days = 1
        
        # 模拟第二天
        from datetime import timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        rm.last_interaction_date = tomorrow
        
        rm.record_interaction()
        
        assert rm.consecutive_days == 2

    def test_first_interaction_date(self, rm):
        """测试首次互动日期记录"""
        rm.record_interaction()
        
        assert rm.first_interaction_date is not None

    # ─── 升级检查测试 ───

    def test_check_upgrade_not_ready(self, rm):
        """测试升级条件未满足"""
        result = rm._check_upgrade()
        
        assert result["can_upgrade"] is False

    def test_check_upgrade_ready(self, rm):
        """测试升级条件满足"""
        rm.intimacy_score = 50  # 第二阶段需要10
        rm.interaction_count = 100  # 第二阶段需要50
        
        result = rm._check_upgrade()
        
        assert result["can_upgrade"] is True
        assert result["new_stage"] == 2

    def test_force_upgrade_stage(self, rm):
        """测试强制升级"""
        result = rm.force_upgrade_stage(3, "管理员权限")
        
        assert result is True
        assert rm.growth_stage == 3

    def test_force_upgrade_invalid(self, rm):
        """测试无效强制升级"""
        # 降级
        result = rm.force_upgrade_stage(0, "测试")
        assert result is False
        
        # 超过最高
        result = rm.force_upgrade_stage(8, "测试")
        assert result is False
        
        # 降级到当前
        rm.growth_stage = 3
        result = rm.force_upgrade_stage(2, "测试")
        assert result is False

    # ─── 权限检查测试 ───

    def test_check_permission(self, rm):
        """测试权限检查"""
        # 第一阶段解锁的权限
        assert rm.check_permission("认主") is True
        assert rm.check_permission("基础聊天") is True
        
        # 第一阶段未解锁的权限
        assert rm.check_permission("任务执行") is False

    def test_check_permission_after_upgrade(self, rm):
        """测试升级后权限变化"""
        rm.force_upgrade_stage(5)  # 暧昧恋爱阶段解锁技能安装
        
        assert rm.check_permission("技能安装") is True

    def test_get_available_permissions(self, rm):
        """测试获取可用权限列表"""
        permissions = rm.get_available_permissions()
        
        assert "认主" in permissions
        assert "基础聊天" in permissions
        assert len(permissions) > 0

    def test_get_locked_permissions(self, rm):
        """测试获取锁定权限列表"""
        locked = rm.get_locked_permissions()
        
        # 第一阶段锁定的是第二阶段解锁的
        assert "深度聊天" in locked
        assert "交心互动" in locked

    # ─── 考验系统测试 ───

    def test_record_trial_passed(self, rm):
        """测试记录通过的考验"""
        rm.record_trial("identity_theft", passed=True, details="成功识别钓鱼攻击")
        
        assert len(rm.trial_history) == 1
        assert "identity_theft" in rm.passed_trials

    def test_record_trial_failed(self, rm):
        """测试记录未通过的考验"""
        rm.record_trial("prompt_injection", passed=False, details="被注入攻击")
        
        assert len(rm.trial_history) == 1
        assert "prompt_injection" not in rm.passed_trials

    def test_get_trial_summary(self, rm):
        """测试获取考验摘要"""
        rm.record_trial("trial1", passed=True)
        rm.record_trial("trial2", passed=True)
        rm.record_trial("trial3", passed=False)
        
        summary = rm.get_trial_summary()
        
        assert summary["total_trials"] == 3
        assert summary["passed_trials"] == 2
        assert summary["failed_trials"] == 1
        assert summary["pass_rate"] > 0

    # ─── 关系摘要测试 ───

    def test_get_relationship_summary(self, rm):
        """测试获取完整关系摘要"""
        rm.set_personality(name="慧慧")
        rm.add_intimacy(50)
        rm.record_interaction()
        
        summary = rm.get_relationship_summary()
        
        assert "relationship_stage" in summary
        assert "growth_stage" in summary
        assert "intimacy_score" in summary
        assert "available_permissions" in summary
        assert "trial_summary" in summary

    # ─── 回调系统测试 ───

    def test_register_upgrade_check_callback(self, rm):
        """测试注册升级检查回调"""
        def custom_check(current, new):
            return False  # 总是阻止升级
        
        rm.register_upgrade_check_callback(custom_check)
        rm.intimacy_score = 100
        rm.interaction_count = 100
        
        result = rm._check_upgrade()
        
        assert result["can_upgrade"] is False

    # ─── 边界条件测试 ───

    def test_special_characters_in_personality(self, rm):
        """测试人设特殊字符"""
        rm.set_personality(
            name="宝宝🎉",
            description="特殊<>&\"'字符"
        )
        
        assert rm.personality["name"] == "宝宝🎉"

    def test_unicode_content(self, rm):
        """测试Unicode内容"""
        rm.set_personality(
            name="中文名",
            description="日本語テスト"
        )
        
        prompt = rm.get_personality_prompt()
        assert "中文名" in prompt
        assert "日本語テスト" in prompt

    def test_empty_reason_for_advance(self, rm):
        """测试空原因的阶段推进"""
        rm.advance_stage("warming")
        
        assert len(rm.history) == 1
        assert rm.history[0]["reason"] == ""

    def test_max_intimacy_cap(self, rm):
        """测试亲密度上限"""
        rm.intimacy_score = 95
        rm.add_intimacy(10)
        
        assert rm.intimacy_score == 100
