"""NVIDIA, Ollama, LiteLLM and OpenAI all speak the OpenAI chat API, so one client fits all.

Pick a preset with LLM_PROVIDER; override LLM_MODEL / LLM_BASE_URL / LLM_API_KEY as needed.
The default models below support tool calling; model catalogs change, so check your provider.
"""

from dataclasses import dataclass

from openai import AsyncOpenAI

from common.config import Settings, get_settings

# provider -> (base_url, default_model, name of the Settings field holding its key or None)
PRESETS: dict[str, tuple[str, str, str | None]] = {
    "nvidia": ("https://integrate.api.nvidia.com/v1", "meta/llama-3.3-70b-instruct", "nvidia_api_key"),
    "ollama": ("http://localhost:11434/v1", "llama3.1", None),  # local, no key needed
    "litellm": ("http://localhost:4000/v1", "local-llm", "litellm_api_key"),
    "openai": ("https://api.openai.com/v1", "gpt-4o-mini", "openai_api_key"),
}


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    base_url: str
    model: str
    api_key: str


def resolve_llm_config(settings: Settings | None = None) -> LLMConfig:
    settings = settings or get_settings()
    provider = settings.llm_provider.lower()
    if provider not in PRESETS:
        raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Choose one of: {', '.join(PRESETS)}")
    base_url, model, key_field = PRESETS[provider]
    key = settings.llm_api_key or (getattr(settings, key_field) if key_field else "ollama")
    if not key:
        raise RuntimeError(f"No API key for provider '{provider}'. Set {(key_field or '').upper()} in .env.")
    return LLMConfig(provider, settings.llm_base_url or base_url, settings.llm_model or model, key)


def get_llm_client(config: LLMConfig | None = None) -> AsyncOpenAI:
    config = config or resolve_llm_config()
    return AsyncOpenAI(base_url=config.base_url, api_key=config.api_key)
