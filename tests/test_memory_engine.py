"""
SoulForge 记忆引擎测试

测试 MemoryEngine 的所有核心功能：
- 核心记忆读写
- 对话日志记录
- 工作记忆管理
- 上下文构建
- 记忆指纹
- 记忆统计
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

from soulforge.core.memory_engine import MemoryEngine, MemoryEntry


class TestMemoryEntry:
    """测试 MemoryEntry 数据类"""

    def test_create_memory_entry(self):
        """测试创建记忆条目"""
        entry = MemoryEntry(content="测试内容", category="test")
        assert entry.content == "测试内容"
        assert entry.category == "test"
        assert entry.importance == 3
        assert entry.timestamp is not None

    def test_memory_entry_with_all_fields(self):
        """测试带所有字段的记忆条目"""
        entry = MemoryEntry(
            content="完整测试",
            category="identity",
            importance=5,
            tags=["重要", "测试"]
        )
        assert entry.importance == 5
        assert entry.tags == ["重要", "测试"]

    def test_memory_entry_to_dict(self):
        """测试转换为字典"""
        entry = MemoryEntry(content="测试", category="event", importance=4)
        data = entry.to_dict()
        assert data["content"] == "测试"
        assert data["category"] == "event"
        assert data["importance"] == 4
        assert "timestamp" in data
        assert "tags" in data

    def test_memory_entry_from_dict(self):
        """测试从字典创建"""
        data = {
            "content": "恢复测试",
            "timestamp": "2024-01-01T00:00:00",
            "category": "emotion",
            "importance": 2,
            "tags": ["恢复"]
        }
        entry = MemoryEntry.from_dict(data)
        assert entry.content == "恢复测试"
        assert entry.category == "emotion"
        assert entry.importance == 2


class TestMemoryEngine:
    """测试 MemoryEngine 核心功能"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def engine(self, temp_dir):
        """创建记忆引擎实例"""
        return MemoryEngine(memory_dir=temp_dir)

    # ─── 核心记忆测试 ───

    def test_init_creates_directories(self, temp_dir):
        """测试初始化创建目录"""
        engine = MemoryEngine(memory_dir=temp_dir)
        assert Path(temp_dir).exists()
        assert (Path(temp_dir) / "logs").exists()

    def test_save_and_load_core_memory(self, engine):
        """测试核心记忆的保存和加载"""
        content = "# 身份档案\n\n我是SoulForge AI助手。"
        engine.save_core_memory(content)
        
        loaded = engine.load_core_memory()
        assert loaded == content

    def test_load_nonexistent_core_memory(self, engine):
        """测试加载不存在的核心记忆"""
        loaded = engine.load_core_memory()
        assert loaded == ""

    def test_append_core_memory_new_section(self, engine):
        """测试追加新章节到核心记忆"""
        engine.save_core_memory("# 身份\n\n初始内容")
        engine.append_core_memory("兴趣", "我喜欢学习新知识")
        
        loaded = engine.load_core_memory()
        assert "## 兴趣" in loaded
        assert "我喜欢学习新知识" in loaded

    def test_append_core_memory_existing_section(self, engine):
        """测试追加内容到已存在的章节"""
        engine.save_core_memory("# 身份\n\n## 兴趣\n\n- 读书\n\n## 习惯")
        engine.append_core_memory("兴趣", "也喜欢运动")
        
        loaded = engine.load_core_memory()
        assert "也喜欢运动" in loaded
        # 验证不是重复添加同一章节
        assert loaded.count("## 兴趣") == 1

    def test_append_core_memory_empty_initial(self, engine):
        """测试初始为空时追加章节"""
        engine.append_core_memory("新章节", "新内容")
        
        loaded = engine.load_core_memory()
        assert "## 新章节" in loaded
        assert "新内容" in loaded

    # ─── 对话日志测试 ───

    def test_log_conversation(self, engine):
        """测试对话日志记录"""
        engine.log_conversation("user", "你好")
        engine.log_conversation("AI", "你好呀！")
        
        logs = engine.get_recent_logs(days=1)
        assert "你好" in logs
        assert "你好呀！" in logs
        assert "user" in logs
        assert "AI" in logs

    def test_log_conversation_with_summary(self, engine):
        """测试带摘要的对话日志"""
        engine.log_conversation("user", "今天心情不好", summary="用户表达了负面情绪")
        
        logs = engine.get_recent_logs(days=1)
        assert "心情不好" in logs
        assert "摘要" in logs

    def test_get_recent_logs_multiple_days(self, engine):
        """测试获取多天日志"""
        # 模拟多天日志
        for _ in range(3):
            engine.log_conversation("user", "测试消息")
        
        logs = engine.get_recent_logs(days=7)
        assert len(logs) > 0

    def test_get_recent_logs_empty(self, engine):
        """测试获取空日志"""
        logs = engine.get_recent_logs(days=1)
        assert logs == ""

    # ─── 工作记忆测试 ───

    def test_add_working_memory(self, engine):
        """测试添加工作记忆"""
        engine.add_working_memory("测试记忆", "test")
        
        working = engine.get_working_memory()
        assert len(working) == 1
        assert working[0].content == "测试记忆"

    def test_add_multiple_working_memory(self, engine):
        """测试添加多条工作记忆"""
        engine.add_working_memory("记忆1", "cat1")
        engine.add_working_memory("记忆2", "cat2")
        engine.add_working_memory("记忆3", "cat1")
        
        working = engine.get_working_memory()
        assert len(working) == 3

    def test_clear_working_memory(self, engine):
        """测试清空工作记忆"""
        engine.add_working_memory("测试", "test")
        engine.add_working_memory("测试2", "test")
        engine.clear_working_memory()
        
        assert len(engine.get_working_memory()) == 0

    def test_working_memory_persistence(self, engine):
        """测试工作记忆不持久化（会话级别）"""
        engine.add_working_memory("会话记忆", "session")
        
        # 创建新实例
        new_engine = MemoryEngine(memory_dir=engine.memory_dir)
        assert len(new_engine.get_working_memory()) == 0

    # ─── 上下文构建测试 ───

    def test_build_context_empty(self, engine):
        """测试空上下文构建"""
        context = engine.build_context()
        assert context == ""

    def test_build_context_with_core_memory(self, engine):
        """测试带核心记忆的上下文"""
        engine.save_core_memory("# 测试\n\n测试内容")
        context = engine.build_context(include_daily=False)
        
        assert "核心记忆" in context
        assert "测试内容" in context

    def test_build_context_with_daily_memory(self, engine):
        """测试带日常记忆的上下文"""
        engine.log_conversation("user", "今天学了很多")
        context = engine.build_context(include_daily=True, daily_days=1)
        
        assert "近期记忆" in context
        assert "今天学了很多" in context

    def test_build_context_with_working_memory(self, engine):
        """测试带工作记忆的上下文"""
        engine.add_working_memory("当前会话信息", "current")
        context = engine.build_context(include_daily=False)
        
        assert "当前记忆" in context
        assert "当前会话信息" in context

    def test_build_context_full(self, engine):
        """测试完整上下文构建"""
        engine.save_core_memory("# 身份\n\n我是AI")
        engine.log_conversation("user", "测试对话")
        engine.add_working_memory("会话中获取的信息", "temp")
        
        context = engine.build_context()
        
        assert "核心记忆" in context
        assert "近期记忆" in context
        assert "当前记忆" in context

    # ─── 记忆指纹测试 ───

    def test_compute_memory_fingerprint(self, engine):
        """测试记忆指纹计算"""
        engine.save_core_memory("初始内容")
        engine.log_conversation("user", "测试")
        
        fingerprint = engine.compute_memory_fingerprint()
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16

    def test_fingerprint_changes_with_content(self, engine):
        """测试内容变化时指纹变化"""
        engine.save_core_memory("内容A")
        fp1 = engine.compute_memory_fingerprint()
        
        engine.save_core_memory("内容B")
        fp2 = engine.compute_memory_fingerprint()
        
        assert fp1 != fp2

    def test_fingerprint_empty_memory(self, engine):
        """测试空记忆的指纹"""
        fingerprint = engine.compute_memory_fingerprint()
        
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16

    # ─── 统计信息测试 ───

    def test_get_stats_empty(self, engine):
        """测试空记忆统计"""
        stats = engine.get_stats()
        
        assert "core_memory_size_bytes" in stats
        assert "core_memory_exists" in stats
        assert "daily_log_count" in stats
        assert "working_memory_entries" in stats
        assert "memory_fingerprint" in stats
        assert stats["daily_log_count"] == 0

    def test_get_stats_with_data(self, engine):
        """测试有数据时的统计"""
        engine.save_core_memory("# 测试\n\n测试内容")
        engine.log_conversation("user", "测试")
        engine.add_working_memory("测试", "test")
        
        stats = engine.get_stats()
        
        assert stats["core_memory_exists"] is True
        assert stats["core_memory_size_bytes"] > 0
        assert stats["daily_log_count"] == 1
        assert stats["working_memory_entries"] == 1

    # ─── 边界条件测试 ───

    def test_special_characters_in_memory(self, engine):
        """测试特殊字符处理"""
        special_content = "# 特殊字符\n\n中文🎉Emoji😀\n特殊<>&\"'\n换行\n\t制表"
        engine.save_core_memory(special_content)
        
        loaded = engine.load_core_memory()
        assert loaded == special_content

    def test_very_long_content(self, engine):
        """测试超长内容"""
        long_content = "x" * 100000
        engine.save_core_memory(long_content)
        
        loaded = engine.load_core_memory()
        assert len(loaded) == 100000

    def test_unicode_content(self, engine):
        """测试Unicode内容"""
        unicode_content = "中文测试\n日本語テスト\n한국어 테스트\n🎉🎊💖"
        engine.save_core_memory(unicode_content)
        
        loaded = engine.load_core_memory()
        assert loaded == unicode_content

    def test_multiple_context_builds(self, engine):
        """测试多次构建上下文"""
        engine.save_core_memory("# 测试")
        engine.add_working_memory("数据1", "cat1")
        
        # 多次构建不应累积
        context1 = engine.build_context()
        engine.add_working_memory("数据2", "cat2")
        context2 = engine.build_context()
        
        assert context1 != context2
