"""Model and provider management for the AI Code Agent Benchmark wizard."""

import os
from typing import Dict, List, Optional
import httpx


class ModelSelector:
    """Handles model provider selection and dynamic model fetching."""

    PROVIDERS = {
        "1": {
            "name": "OpenRouter (Access to 100+ models)",
            "key": "OPEN_ROUTER_API_KEY",
        },
        "2": {"name": "OpenAI (GPT-4o, GPT-3.5)", "key": "OPENAI_API_KEY"},
        "3": {"name": "Anthropic (Claude 3.5 Sonnet)", "key": "ANTHROPIC_API_KEY"},
        "4": {"name": "Google Gemini (Gemini 1.5 Pro/Flash)", "key": "GEMINI_API_KEY"},
    }

    MODEL_LISTS = {
        "2": [
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        ],
        "3": [
            {"id": "claude-3-5-sonnet-20240620", "name": "Claude 3.5 Sonnet"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
        ],
        "4": [
            {"id": "gemini/gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
            {"id": "gemini/gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
        ],
    }

    def fetch_openrouter_models(self) -> List[Dict[str, str]]:
        """Fetch available models from OpenRouter."""
        try:
            response = httpx.get("https://openrouter.ai/api/v1/models", timeout=10)
            response.raise_for_status()
            data = response.json()
            models = []
            for m in data.get("data", []):
                # Filter for some common coding models if list is too long
                m_id = m.get("id", "")
                if not m_id.startswith("openrouter/"):
                    m_id = f"openrouter/{m_id}"
                name = m.get("name", m_id)
                models.append({"id": m_id, "name": name})
            return models[:20]  # Just show top 20
        except Exception:
            return [
                {
                    "id": "openrouter/google/gemini-2.0-flash-exp:free",
                    "name": "Gemini 2.0 Flash (Free)",
                },
                {
                    "id": "openrouter/anthropic/claude-3.5-sonnet",
                    "name": "Claude 3.5 Sonnet",
                },
                {
                    "id": "openrouter/meta-llama/llama-3.1-405b-instruct",
                    "name": "Llama 3.1 405B",
                },
            ]

    def get_models_for_provider(self, provider_id: str) -> List[Dict[str, str]]:
        """Get the list of models for a specific provider."""
        if provider_id == "1":
            return self.fetch_openrouter_models()
        return self.MODEL_LISTS.get(provider_id, [])

    def check_api_key(self, provider_id: str) -> Optional[str]:
        """Return the API key name if it's missing from the environment."""
        key_name = self.PROVIDERS.get(provider_id, {}).get("key")
        if key_name and not os.getenv(key_name):
            return key_name
        return None
