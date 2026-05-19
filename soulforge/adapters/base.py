"""Base adapter for SoulForge."""

from abc import ABC, abstractmethod
from typing import Optional


class BaseModelAdapter(ABC):
    """模型适配器基类"""

    @abstractmethod
    def chat(self, messages: list[dict], system_prompt: str = "",
             temperature: float = 0.7) -> str:
        """发送对话请求"""
        pass

    @abstractmethod
    def stream_chat(self, messages: list[dict], system_prompt: str = "",
                    temperature: float = 0.7):
        """流式对话"""
        pass
