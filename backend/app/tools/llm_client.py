"""LLM client: multi-provider OpenAI-compatible API integration."""

import json
import httpx
from app.core.config import settings
from app.core.logging import logger

PROVIDER_CONFIGS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "openai-compatible": {
        "base_url": "",
        "default_model": "gpt-4o-mini",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
}


class LLMClient:
    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self._provider = settings.llm_provider or "openai"
        self._available = bool(settings.llm_api_key)

        config = PROVIDER_CONFIGS.get(self._provider, PROVIDER_CONFIGS["openai"])
        self._base_url = settings.llm_base_url or config["base_url"]
        self._default_model = settings.llm_model or config["default_model"]
        self._auth_header = config["auth_header"]
        self._auth_prefix = config["auth_prefix"]

    @property
    def available(self) -> bool:
        return self._available

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._default_model

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def chat(
        self,
        messages: list[dict],
        model: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: dict | None = None,
    ) -> dict:
        """Send a chat completion request."""
        if not self._available:
            return {"success": False, "content": "", "error": "LLM not configured"}

        model_name = model or self._default_model

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            client = await self._get_client()
            response = await client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers={
                    self._auth_header: f"{self._auth_prefix}{settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"]
            return {"success": True, "content": content, "error": None}

        except httpx.HTTPError as e:
            logger.error(f"LLM API request failed ({self._provider}): {e}")
            return {"success": False, "content": "", "error": str(e)}
        except (KeyError, IndexError) as e:
            logger.error(f"LLM response parse error ({self._provider}): {e}")
            return {"success": False, "content": "", "error": f"Response parse error: {e}"}

    async def chat_json(
        self,
        messages: list[dict],
        model: str = "",
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> dict:
        """Send a chat request and parse JSON response."""
        result = await self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        if not result["success"]:
            return result

        try:
            parsed = json.loads(result["content"])
            return {"success": True, "content": parsed, "error": None}
        except json.JSONDecodeError:
            content = result["content"]
            try:
                start = content.index("{")
                end = content.rindex("}") + 1
                parsed = json.loads(content[start:end])
                return {"success": True, "content": parsed, "error": None}
            except (ValueError, json.JSONDecodeError):
                return {"success": False, "content": "", "error": "Failed to parse JSON from LLM response"}

    async def embed(
        self,
        texts: list[str],
        model: str = "",
    ) -> dict:
        """Get embeddings for texts. Uses OpenAI-compatible embeddings API."""
        if not self._available:
            return {"success": False, "embeddings": [], "error": "LLM not configured"}

        model_name = model or settings.embedding_model or "text-embedding-3-small"

        try:
            client = await self._get_client()
            response = await client.post(
                f"{self._base_url}/embeddings",
                json={
                    "model": model_name,
                    "input": texts,
                },
                headers={
                    self._auth_header: f"{self._auth_prefix}{settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()

            embeddings = [item["embedding"] for item in data["data"]]
            return {"success": True, "embeddings": embeddings, "error": None}

        except httpx.HTTPError as e:
            logger.error(f"Embedding API request failed ({self._provider}): {e}")
            return {"success": False, "embeddings": [], "error": str(e)}

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


llm_client = LLMClient()
