"""Local model adapter (Ollama, etc.)."""

from .base import BaseModelAdapter


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
