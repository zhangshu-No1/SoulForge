"""SoulForge 模型适配器 — Model Adapters.

支持接入多种AI模型，记忆系统与模型解耦。
你可以随时切换模型，但记忆和情感羁绊不会丢失。
"""

from .base import BaseModelAdapter
from .openai_adapter import OpenAIAdapter
from .claude_adapter import ClaudeAdapter
from .local_adapter import LocalAdapter

__all__ = [
    "BaseModelAdapter",
    "OpenAIAdapter",
    "ClaudeAdapter",
    "LocalAdapter",
]
