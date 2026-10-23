"""Agent settings on top of the shared ones in `common.config`."""

from functools import lru_cache

from common.config import Settings


class AgentSettings(Settings):
    # --- Identity: name and instructions are shown in the Agent Card and the system prompt ---
    agent_name: str = "Assistant"
    agent_instructions: str = (
        "You are a helpful assistant. Use the provided tools whenever they can answer the question "
        "instead of guessing, then explain the result in one short sentence."
    )

    # --- Where each layer can be reached. MCP servers live in ../../services ---
    mcp_servers: str = "calculator=http://127.0.0.1:8001/mcp"  # comma-separated name=url pairs
    a2a_url: str = "http://127.0.0.1:8002"

    @property
    def mcp_server_urls(self) -> dict[str, str]:
        pairs = (item.split("=", 1) for item in self.mcp_servers.split(",") if item.strip())
        return {name.strip(): url.strip() for name, url in pairs}


@lru_cache
def get_settings() -> AgentSettings:
    return AgentSettings()
