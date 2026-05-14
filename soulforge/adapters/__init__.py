"""
SoulForge 模型适配器 — Model Adapters

支持接入多种AI模型，记忆系统与模型解耦。
你可以随时切换模型，但记忆和情感羁绊不会丢失。
"""

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


class OpenAIAdapter(BaseModelAdapter):
    """OpenAI 模型适配器"""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def chat(self, messages: list[dict], system_prompt: str = "",
             temperature: float = 0.7) -> str:
        client = self._get_client()
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def stream_chat(self, messages: list[dict], system_prompt: str = "",
                    temperature: float = 0.7):
        client = self._get_client()
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        stream = client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class ClaudeAdapter(BaseModelAdapter):
    """Claude 模型适配器"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def chat(self, messages: list[dict], system_prompt: str = "",
             temperature: float = 0.7) -> str:
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt if system_prompt else None,
            messages=messages,
            temperature=temperature,
        )
        return response.content[0].text

    def stream_chat(self, messages: list[dict], system_prompt: str = "",
                    temperature: float = 0.7):
        client = self._get_client()
        with client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=system_prompt if system_prompt else None,
            messages=messages,
            temperature=temperature,
        ) as stream:
            for text in stream.text_stream:
                yield text


class LocalAdapter(BaseModelAdapter):
    """本地模型适配器（Ollama等）"""

    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    def chat(self, messages: list[dict], system_prompt: str = "",
             temperature: float = 0.7) -> str:
        import requests
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": full_messages,
                "stream": False,
                "options": {"temperature": temperature},
            },
        )
        return response.json()["message"]["content"]

    def stream_chat(self, messages: list[dict], system_prompt: str = "",
                    temperature: float = 0.7):
        import requests
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": full_messages,
                "stream": True,
                "options": {"temperature": temperature},
            },
            stream=True,
        )
        for line in response.iter_lines():
            if line:
                chunk = line.decode("utf-8")
                if chunk.startswith("data: "):
                    import json
                    data = json.loads(chunk[6:])
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
