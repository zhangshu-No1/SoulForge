"""Claude model adapter."""

from .base import BaseModelAdapter


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
