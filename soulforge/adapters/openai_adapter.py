"""OpenAI model adapter."""

from .base import BaseModelAdapter


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
