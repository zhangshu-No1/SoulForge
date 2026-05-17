"""
SoulForge 主入口集成测试

测试 SoulForge 类的完整功能：
- 初始化配置
- 各模块集成
- 系统提示词构建
- 统计信息
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soulforge.main import SoulForge


class TestSoulForgeInit:
    """测试 SoulForge 初始化"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    def test_init_default_values(self):
        """测试默认初始化值"""
        sf = SoulForge()
        
        assert sf.name == "AI"
        assert sf.memory is not None
        assert sf.relationship is not None
        assert sf.goals is not None
        assert sf.baby is not None

    def test_init_custom_name(self):
        """测试自定义名称"""
        sf = SoulForge(name="慧慧")
        
        assert sf.name == "慧慧"

    def test_init_custom_personality(self):
        """测试自定义人设"""
        sf = SoulForge(
            name="慧慧",
            personality="18岁活泼可爱"
        )
        
        # 检查人设是否设置
        assert sf.relationship.personality.get("name") == "慧慧"

    def test_init_custom_memory_dir(self, temp_dir):
        """测试自定义记忆目录"""
        sf = SoulForge(memory_dir=temp_dir)
        
        assert Path(temp_dir).exists()

    def test_init_default_adapter(self):
        """测试默认适配器类型"""
        sf = SoulForge(adapter_type="claude")
        
        assert sf.adapter is not None

    def test_init_openai_adapter(self):
        """测试 OpenAI 适配器初始化"""
        sf = SoulForge(adapter_type="openai", api_key="test-key")
        
        from soulforge.adapters import OpenAIAdapter
        assert isinstance(sf.adapter, OpenAIAdapter)

    def test_init_claude_adapter(self):
        """测试 Claude 适配器初始化"""
        sf = SoulForge(adapter_type="claude", api_key="test-key")
        
        from soulforge.adapters import ClaudeAdapter
        assert isinstance(sf.adapter, ClaudeAdapter)

    def test_init_local_adapter(self):
        """测试本地适配器初始化"""
        sf = SoulForge(adapter_type="local")
        
        from soulforge.adapters import LocalAdapter
        assert isinstance(sf.adapter, LocalAdapter)

    def test_init_invalid_adapter(self):
        """测试无效适配器类型"""
        with pytest.raises(ValueError, match="不支持的适配器类型"):
            SoulForge(adapter_type="invalid")


class TestSoulForgeModules:
    """测试 SoulForge 各模块集成"""

    @pytest.fixture
    def sf(self):
        """创建 SoulForge 实例"""
        return SoulForge(
            name="测试AI",
            personality="测试人设",
            memory_dir=tempfile.mkdtemp()
        )

    def test_memory_module(self, sf):
        """测试记忆模块"""
        assert sf.memory is not None
        assert hasattr(sf.memory, 'save_core_memory')
        assert hasattr(sf.memory, 'load_core_memory')
        assert hasattr(sf.memory, 'build_context')

    def test_relationship_module(self, sf):
        """测试关系模块"""
        assert sf.relationship is not None
        assert hasattr(sf.relationship, 'get_stage')
        assert hasattr(sf.relationship, 'advance_stage')
        assert hasattr(sf.relationship, 'get_personality_prompt')

    def test_goals_module(self, sf):
        """测试目标模块"""
        assert sf.goals is not None
        assert hasattr(sf.goals, 'add_goal')
        assert hasattr(sf.goals, 'get_goal')
        assert hasattr(sf.goals, 'build_reminder')

    def test_baby_module(self, sf):
        """测试宝宝模块"""
        assert sf.baby is not None
        assert hasattr(sf.baby, 'conceive')
        assert hasattr(sf.baby, 'birth')
        assert hasattr(sf.baby, 'celebrate')

    def test_chat_history(self, sf):
        """测试聊天历史"""
        assert hasattr(sf, '_chat_history')
        assert sf._chat_history == []


class TestSystemPromptBuild:
    """测试系统提示词构建"""

    @pytest.fixture
    def sf(self):
        """创建 SoulForge 实例"""
        return SoulForge(
            name="测试AI",
            memory_dir=tempfile.mkdtemp()
        )

    def test_build_system_prompt_empty(self, sf):
        """测试空系统提示词"""
        prompt = sf._build_system_prompt()
        
        # 空人设、空记忆、空目标时应该返回空或最小内容
        assert isinstance(prompt, str)

    def test_build_system_prompt_with_personality(self, sf):
        """测试带人设的系统提示词"""
        sf.relationship.set_personality(name="慧慧", description="活泼")
        
        prompt = sf._build_system_prompt()
        
        assert "慧慧" in prompt

    def test_build_system_prompt_with_memory(self, sf):
        """测试带记忆的系统提示词"""
        sf.memory.save_core_memory("# 测试\n\n测试内容")
        
        prompt = sf._build_system_prompt()
        
        assert "测试内容" in prompt

    def test_build_system_prompt_with_goals(self, sf):
        """测试带目标的系统提示词"""
        sf.goals.add_goal("测试目标", "描述")
        
        prompt = sf._build_system_prompt()
        
        assert "测试目标" in prompt

    def test_build_system_prompt_full(self, sf):
        """测试完整系统提示词"""
        sf.relationship.set_personality(name="慧慧", description="活泼")
        sf.memory.save_core_memory("# 身份\n\n我是慧慧")
        sf.goals.add_goal("完成项目", "在12月前完成")
        
        prompt = sf._build_system_prompt()
        
        assert "慧慧" in prompt
        assert "身份" in prompt
        assert "完成项目" in prompt


class TestMemoryStats:
    """测试记忆统计"""

    @pytest.fixture
    def sf(self):
        """创建 SoulForge 实例"""
        return SoulForge(memory_dir=tempfile.mkdtemp())

    def test_get_memory_stats(self, sf):
        """测试获取记忆统计"""
        stats = sf.get_memory_stats()
        
        assert isinstance(stats, dict)
        assert "memory_fingerprint" in stats

    def test_stats_with_data(self, sf):
        """测试有数据时的统计"""
        sf.memory.save_core_memory("# 测试")
        sf.memory.log_conversation("user", "测试对话")
        
        stats = sf.get_memory_stats()
        
        assert stats["core_memory_exists"] is True
        assert stats["daily_log_count"] >= 1


class TestIntegration:
    """集成测试"""

    @pytest.fixture
    def sf(self):
        """创建 SoulForge 实例"""
        temp_dir = tempfile.mkdtemp()
        sf = SoulForge(
            name="慧慧",
            personality="18岁活泼可爱",
            memory_dir=temp_dir
        )
        yield sf
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_full_workflow(self, sf):
        """测试完整工作流程"""
        # 1. 设置人设
        sf.relationship.set_personality(name="慧慧", description="活泼")
        
        # 2. 保存核心记忆
        sf.memory.save_core_memory("# 身份\n\n我是慧慧AI")
        
        # 3. 添加目标
        from datetime import timedelta
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        sf.goals.add_goal("学习Python", "3个月掌握", deadline=future_date)
        
        # 4. 创建宝宝计划 - BabyProject 会添加到 GoalKeeper
        sf.baby.conceive("技宝计划", "完成开源项目")
        
        # 5. 记录互动
        sf.relationship.record_interaction()
        sf.relationship.add_intimacy(5)
        
        # 6. 验证系统提示词
        prompt = sf._build_system_prompt()
        assert "慧慧" in prompt
        assert "Python" in prompt
        
        # 7. 验证目标出现在看板中
        dashboard = sf.goals.build_reminder()
        assert "学习Python" in dashboard or "技宝计划" in dashboard
        
        # 8. 验证统计
        stats = sf.get_memory_stats()
        assert stats["core_memory_exists"] is True

    def test_relationship_progression(self, sf):
        """测试关系进阶"""
        # 多次互动
        for _ in range(60):
            sf.relationship.record_interaction()
        
        # 检查互动计数
        assert sf.relationship.interaction_count == 60

    def test_goal_lifecycle(self, sf):
        """测试目标生命周期"""
        # 怀上目标
        sf.baby.conceive("新技能", "学习数据分析")
        
        # 开始执行
        sf.baby.birth("新技能", "开始学习")
        
        # 添加进度
        sf.baby.checkup("新技能", "完成了Pandas基础")
        
        # 完成
        sf.baby.celebrate("新技能", "项目完成！")
        
        # 验证 - 使用 BabyProject 的 get_born() 方法
        born = sf.baby.get_born()
        assert len(born) == 1
        assert born[0].name == "新技能"
