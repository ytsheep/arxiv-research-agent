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
        """Get embeddings for texts using local BGE-M3 model."""
        from app.tools.local_embedding import embed_batch
        embeddings = embed_batch(texts)
        if embeddings:
            return {"success": True, "embeddings": embeddings, "error": None}
        return {"success": False, "embeddings": [], "error": "Local embedding model not available"}

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        model: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> dict:
        """Send a chat completion request with tool/function definitions.
        Returns tool_calls from the response, or a text response if no tool is called."""
        if not self._available:
            return {"success": False, "content": "", "tool_calls": [], "error": "LLM not configured"}

        model_name = model or self._default_model

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "tools": tools,
        }

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

            choice = data["choices"][0]
            message = choice.get("message", {})

            tool_calls = message.get("tool_calls", [])
            content = message.get("content", "")

            return {
                "success": True,
                "content": content,
                "tool_calls": tool_calls,
                "error": None,
            }

        except httpx.HTTPError as e:
            logger.error(f"LLM tool-calling request failed ({self._provider}): {e}")
            return {"success": False, "content": "", "tool_calls": [], "error": str(e)}
        except (KeyError, IndexError) as e:
            logger.error(f"LLM tool-calling response parse error: {e}")
            return {"success": False, "content": "", "tool_calls": [], "error": str(e)}

    async def plan_with_tools(
        self,
        user_message: str,
        state_summary: str,
        tools: list[dict],
        model: str = "",
    ) -> dict:
        """Plan the next ReAct step. Returns a structured decision:
        {"reasoning_summary": str, "action": str, "arguments": dict}

        'action' is either a tool name or 'final_answer'."""
        if not self._available:
            return {
                "success": False,
                "reasoning_summary": "LLM not available, cannot plan",
                "action": "final_answer",
                "arguments": {},
                "error": "LLM not configured",
            }

        tool_descriptions = []
        for t in tools:
            func = t.get("function", {})
            tool_descriptions.append(
                f"- {func.get('name', '')}: {func.get('description', '')}"
            )

        system_prompt = f"""You are a controlled ReAct Agent for an arXiv paper assistant.

You must decide the next action to take based on the user's request and the current state. Output a JSON object with your decision.

Available tools:
{chr(10).join(tool_descriptions) if tool_descriptions else '- None (only final_answer available)'}

Rules:
1. Choose ONE action from the available tools, or use "final_answer" when the task is complete.
2. Provide a brief reasoning_summary (one sentence in Chinese).
3. Only use tools listed above. Do not invent tools.
4. Do not call expensive tools (parsing, downloading) during search.
5. If the task is simple, prefer final_answer.
6. max_steps per task is 6.

Current state: {state_summary if state_summary else "Initial step"}

Output exactly this JSON (no extra text):
{{"reasoning_summary": "...", "action": "tool_name or final_answer", "arguments": {{...}}}}"""

        result = await self.chat_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model=model,
            temperature=0.2,
            max_tokens=1024,
        )

        if result["success"] and isinstance(result["content"], dict):
            data = result["content"]
            return {
                "success": True,
                "reasoning_summary": data.get("reasoning_summary", ""),
                "action": data.get("action", "final_answer"),
                "arguments": data.get("arguments", {}),
                "error": None,
            }

        # Fallback: return final_answer
        return {
            "success": False,
            "reasoning_summary": "Failed to plan, returning final answer",
            "action": "final_answer",
            "arguments": {},
            "error": result.get("error", "plan_with_tools failed"),
        }

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


llm_client = LLMClient()
