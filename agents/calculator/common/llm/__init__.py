"""Provider-agnostic LLM access through the OpenAI-compatible API."""

from common.llm.client import LLMConfig, get_llm_client, resolve_llm_config

__all__ = ["LLMConfig", "get_llm_client", "resolve_llm_config"]
