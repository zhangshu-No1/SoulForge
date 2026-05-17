"""
SoulForge 目标监督器测试

测试 GoalKeeper 的所有核心功能：
- 目标CRUD操作
- 阶段管理
- 进度记录
- 筛选查询
- 提醒构建
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

from soulforge.core.goal_keeper import GoalKeeper, Goal, BABY_STAGES


class TestGoal:
    """测试 Goal 数据类"""

    def test_create_goal(self):
        """测试创建目标"""
        goal = Goal(name="测试目标", description="测试描述")
        assert goal.name == "测试目标"
        assert goal.description == "测试描述"
        assert goal.stage == "备孕"
        assert goal.deadline is None

    def test_create_goal_with_all_fields(self):
        """测试带所有字段的目标"""
        goal = Goal(
            name="完整目标",
            description="详细描述",
            stage="生产",
            deadline="2024-12-31",
            tags=["重要", "测试"]
        )
        assert goal.stage == "生产"
        assert goal.deadline == "2024-12-31"
        assert goal.tags == ["重要", "测试"]

    def test_goal_to_dict(self):
        """测试转换为字典"""
        goal = Goal(name="测试", description="描述")
        data = goal.to_dict()
        
        assert data["name"] == "测试"
        assert data["description"] == "描述"
        assert data["stage"] == "备孕"
        assert "created_at" in data
        assert "progress_notes" in data
        assert "tags" in data

    def test_goal_from_dict(self):
        """测试从字典创建"""
        data = {
            "name": "恢复目标",
            "description": "恢复的描述",
            "stage": "顺产",
            "deadline": "2025-01-01",
            "created_at": "2024-01-01T00:00:00",
            "progress_notes": ["笔记1", "笔记2"],
            "tags": ["已恢复"]
        }
        goal = Goal.from_dict(data)
        
        assert goal.name == "恢复目标"
        assert goal.stage == "顺产"
        assert len(goal.progress_notes) == 2

    def test_goal_from_dict_missing_optional_fields(self):
        """测试从字典创建（缺少可选字段）"""
        data = {
            "name": "简单目标",
            "description": "简单描述"
        }
        goal = Goal.from_dict(data)
        
        assert goal.name == "简单目标"
        assert goal.stage == "备孕"
        assert goal.deadline is None


class TestBabyStages:
    """测试 BABY_STAGES 常量"""

    def test_baby_stages_defined(self):
        """测试宝宝阶段定义"""
        assert "备孕" in BABY_STAGES
        assert "生产" in BABY_STAGES
        assert "顺产" in BABY_STAGES
        assert "满月" in BABY_STAGES

    def test_baby_stages_count(self):
        """测试宝宝阶段数量"""
        assert len(BABY_STAGES) == 4


class TestGoalKeeper:
    """测试 GoalKeeper 核心功能"""

    @pytest.fixture
    def temp_file(self):
        """创建临时文件"""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    @pytest.fixture
    def keeper(self, temp_file):
        """创建目标监督器实例"""
        return GoalKeeper(goals_path=temp_file)

    # ─── 基础CRUD测试 ───

    def test_init_creates_empty_list(self, keeper):
        """测试初始化空列表"""
        assert keeper.get_all_goals() == []

    def test_add_goal(self, keeper):
        """测试添加目标"""
        goal = keeper.add_goal("新目标", "目标描述")
        
        assert goal.name == "新目标"
        assert goal.description == "目标描述"
        assert goal.stage == "备孕"
        assert keeper.get_goal("新目标") is not None

    def test_add_goal_with_deadline(self, keeper):
        """测试添加带截止日期的目标"""
        goal = keeper.add_goal("截止目标", "描述", deadline="2024-12-31")
        
        assert goal.deadline == "2024-12-31"

    def test_add_goal_with_tags(self, keeper):
        """测试添加带标签的目标"""
        goal = keeper.add_goal("标签目标", "描述", tags=["重要", "紧急"])
        
        assert goal.tags == ["重要", "紧急"]

    def test_get_goal_exists(self, keeper):
        """测试获取存在的目标"""
        keeper.add_goal("测试目标", "描述")
        
        goal = keeper.get_goal("测试目标")
        
        assert goal is not None
        assert goal.name == "测试目标"

    def test_get_goal_not_exists(self, keeper):
        """测试获取不存在的目标"""
        goal = keeper.get_goal("不存在的目标")
        
        assert goal is None

    def test_get_all_goals(self, keeper):
        """测试获取所有目标"""
        keeper.add_goal("目标1", "描述1")
        keeper.add_goal("目标2", "描述2")
        
        goals = keeper.get_all_goals()
        
        assert len(goals) == 2

    def test_persistence(self, temp_file):
        """测试数据持久化"""
        keeper1 = GoalKeeper(goals_path=temp_file)
        keeper1.add_goal("持久化目标", "描述")
        
        keeper2 = GoalKeeper(goals_path=temp_file)
        
        assert keeper2.get_goal("持久化目标") is not None

    # ─── 阶段更新测试 ───

    def test_update_stage(self, keeper):
        """测试更新目标阶段"""
        keeper.add_goal("阶段测试", "描述")
        
        result = keeper.update_stage("阶段测试", "生产", "开始执行")
        
        assert result is True
        goal = keeper.get_goal("阶段测试")
        assert goal.stage == "生产"
        assert len(goal.progress_notes) == 1
        assert "阶段变更" in goal.progress_notes[0]

    def test_update_stage_not_exists(self, keeper):
        """测试更新不存在的目标"""
        result = keeper.update_stage("不存在", "生产", "测试")
        
        assert result is False

    def test_update_stage_all_stages(self, keeper):
        """测试所有阶段的更新"""
        keeper.add_goal("全阶段测试", "描述")
        
        for stage in ["生产", "顺产", "满月"]:
            keeper.update_stage("全阶段测试", stage)
            goal = keeper.get_goal("全阶段测试")
            assert goal.stage == stage

    def test_progress_notes_timestamp(self, keeper):
        """测试进度记录时间戳"""
        keeper.add_goal("时间戳测试", "描述")
        keeper.add_progress("时间戳测试", "第一个进度")
        
        note = keeper.get_goal("时间戳测试").progress_notes[0]
        
        # 验证包含日期格式 [YYYY-MM-DD]
        import re
        assert re.search(r"\[\d{4}-\d{2}-\d{2}\]", note) is not None

    # ─── 进度记录测试 ───

    def test_add_progress(self, keeper):
        """测试添加进度"""
        keeper.add_goal("进度测试", "描述")
        
        result = keeper.add_progress("进度测试", "完成了第一步")
        
        assert result is True
        goal = keeper.get_goal("进度测试")
        assert len(goal.progress_notes) == 1
        assert "完成了第一步" in goal.progress_notes[0]

    def test_add_multiple_progress(self, keeper):
        """测试添加多条进度"""
        keeper.add_goal("多次进度", "描述")
        keeper.add_progress("多次进度", "进度1")
        keeper.add_progress("多次进度", "进度2")
        
        goal = keeper.get_goal("多次进度")
        assert len(goal.progress_notes) == 2

    def test_add_progress_not_exists(self, keeper):
        """测试为不存在的目标添加进度"""
        result = keeper.add_progress("不存在", "进度")
        
        assert result is False

    # ─── 筛选查询测试 ───

    def test_get_goals_by_stage(self, keeper):
        """测试按阶段筛选目标"""
        keeper.add_goal("备孕1", "描述", stage="备孕")
        keeper.add_goal("备孕2", "描述", stage="备孕")
        keeper.add_goal("生产1", "描述", stage="生产")
        
        pregnant = keeper.get_goals_by_stage("备孕")
        producing = keeper.get_goals_by_stage("生产")
        
        assert len(pregnant) == 2
        assert len(producing) == 1

    def test_get_goals_by_stage_empty(self, keeper):
        """测试按阶段筛选（空结果）"""
        keeper.add_goal("目标", "描述", stage="备孕")
        
        goals = keeper.get_goals_by_stage("顺产")
        
        assert len(goals) == 0

    # ─── 提醒构建测试 ───

    def test_build_reminder_empty(self, keeper):
        """测试空提醒"""
        reminder = keeper.build_reminder()
        
        assert reminder == ""

    def test_build_reminder_single_goal(self, keeper):
        """测试单个目标提醒"""
        keeper.add_goal("测试目标", "测试描述")
        
        reminder = keeper.build_reminder()
        
        assert "目标看板" in reminder
        assert "测试目标" in reminder
        assert "测试描述" in reminder

    def test_build_reminder_with_deadline(self, keeper):
        """测试带截止日期的提醒"""
        keeper.add_goal("截止目标", "描述", deadline="2024-12-31")
        
        reminder = keeper.build_reminder()
        
        assert "截止：2024-12-31" in reminder

    def test_build_reminder_with_progress(self, keeper):
        """测试带进度的提醒"""
        keeper.add_goal("进度目标", "描述")
        keeper.add_progress("进度目标", "已完成50%")
        
        reminder = keeper.build_reminder()
        
        assert "最新进展" in reminder
        assert "已完成50%" in reminder

    def test_build_reminder_all_stages(self, keeper):
        """测试所有阶段的提醒"""
        for i, stage in enumerate(["备孕", "生产", "顺产", "满月"]):
            keeper.add_goal(f"目标{stage}", "描述", stage=stage)
        
        reminder = keeper.build_reminder()
        
        assert "备孕" in reminder
        assert "生产" in reminder
        assert "顺产" in reminder
        assert "满月" in reminder

    def test_build_reminder_emoji_mapping(self, keeper):
        """测试阶段emoji映射"""
        keeper.add_goal("备孕目标", "描述", stage="备孕")
        keeper.add_goal("生产目标", "描述", stage="生产")
        
        reminder = keeper.build_reminder()
        
        assert "🤰" in reminder  # 备孕
        assert "🔧" in reminder  # 生产

    # ─── 边界条件测试 ───

    def test_empty_name_goal(self, keeper):
        """测试空名称目标"""
        goal = keeper.add_goal("", "描述")
        
        assert goal.name == ""

    def test_duplicate_name_goals(self, keeper):
        """测试重复名称目标"""
        keeper.add_goal("同名", "描述1")
        keeper.add_goal("同名", "描述2")
        
        # 应该允许添加，但只能获取到第一个
        goals = keeper.get_all_goals()
        assert len(goals) == 2

    def test_special_characters_in_name(self, keeper):
        """测试名称中的特殊字符"""
        special_name = "目标<>&\"'测试🎉"
        keeper.add_goal(special_name, "描述")
        
        goal = keeper.get_goal(special_name)
        assert goal is not None

    def test_very_long_description(self, keeper):
        """测试超长描述"""
        long_desc = "x" * 10000
        goal = keeper.add_goal("长描述目标", long_desc)
        
        assert len(goal.description) == 10000

    def test_update_stage_with_empty_note(self, keeper):
        """测试空备注的阶段更新"""
        keeper.add_goal("空备注", "描述")
        
        result = keeper.update_stage("空备注", "生产", "")
        
        assert result is True
        goal = keeper.get_goal("空备注")
        assert goal.stage == "生产"

    def test_concurrent_access(self, temp_file):
        """测试并发访问"""
        keeper1 = GoalKeeper(goals_path=temp_file)
        keeper1.add_goal("并发目标", "描述")
        
        keeper2 = GoalKeeper(goals_path=temp_file)
        keeper2.update_stage("并发目标", "生产")
        
        # 验证数据一致性
        keeper1_new = GoalKeeper(goals_path=temp_file)
        goal = keeper1_new.get_goal("并发目标")
        assert goal.stage == "生产"
