"""
SoulForge 模型适配器测试

测试 BaseModelAdapter 和各个具体适配器：
- 基类定义
- 抽象方法存在性
- 错误处理
"""

import os
import sys
from abc import ABC

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from soulforge.adapters import (
    BaseModelAdapter,
    OpenAIAdapter,
    ClaudeAdapter,
    LocalAdapter,
)


class TestBaseModelAdapter:
    """测试 BaseModelAdapter 基类"""

    def test_is_abstract(self):
        """测试是抽象类"""
        assert issubclass(BaseModelAdapter, ABC)

    def test_has_chat_method(self):
        """测试有 chat 抽象方法"""
        assert hasattr(BaseModelAdapter, 'chat')

    def test_has_stream_chat_method(self):
        """测试有 stream_chat 抽象方法"""
        assert hasattr(BaseModelAdapter, 'stream_chat')


class TestOpenAIAdapter:
    """测试 OpenAI 适配器"""

    def test_init(self):
        """测试初始化"""
        adapter = OpenAIAdapter(api_key="test-key", model="gpt-4")
        
        assert adapter.api_key == "test-key"
        assert adapter.model == "gpt-4"

    def test_init_default_model(self):
        """测试默认模型"""
        adapter = OpenAIAdapter(api_key="test-key")
        
        assert adapter.model == "gpt-4o"

    def test_client_lazy_init(self):
        """测试客户端延迟初始化"""
        adapter = OpenAIAdapter(api_key="test-key")
        
        # 尚未初始化
        assert adapter._client is None


class TestClaudeAdapter:
    """测试 Claude 适配器"""

    def test_init(self):
        """测试初始化"""
        adapter = ClaudeAdapter(api_key="test-key", model="claude-3")
        
        assert adapter.api_key == "test-key"
        assert adapter.model == "claude-3"

    def test_init_default_model(self):
        """测试默认模型"""
        adapter = ClaudeAdapter(api_key="test-key")
        
        assert adapter.model == "claude-sonnet-4-20250514"


class TestLocalAdapter:
    """测试本地适配器"""

    def test_init(self):
        """测试初始化"""
        adapter = LocalAdapter(model="llama-2")
        
        assert adapter.model == "llama-2"

    def test_init_default_model(self):
        """测试默认模型"""
        adapter = LocalAdapter()
        
        assert adapter.model == "llama3"
