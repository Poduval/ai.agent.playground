"""The Agent Card: the public "business card" other agents read to learn what this agent does.

Served at /.well-known/agent-card.json (no auth). It declares skills, supported modes
and the security scheme callers must use for the JSON-RPC endpoint.
"""

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.types.a2a_pb2 import HTTPAuthSecurityScheme, SecurityRequirement, SecurityScheme, StringList

from agent import __version__
from agent.config import AgentSettings, get_settings


def build_agent_card(settings: AgentSettings | None = None) -> AgentCard:
    settings = settings or get_settings()
    return AgentCard(
        name=settings.agent_name,
        description=settings.agent_instructions,
        version=__version__,
        documentation_url="https://github.com/Poduval/ai.agent.playground",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=False),
        supported_interfaces=[AgentInterface(protocol_binding="JSONRPC", protocol_version="1.0", url=settings.a2a_url)],
        security_schemes={
            "bearer": SecurityScheme(http_auth_security_scheme=HTTPAuthSecurityScheme(scheme="Bearer", description="Static bearer token"))
        },
        security_requirements=[SecurityRequirement(schemes={"bearer": StringList()})],
        # One skill per configured MCP server: the card stays accurate as servers are added.
        skills=[
            AgentSkill(
                id=name,
                name=f"{name} tools",
                description=f"Ask in plain English; an LLM uses the '{name}' MCP server's tools. Memory is kept per context.",
                tags=["mcp", "llm", "memory"],
                examples=[],
                input_modes=["text/plain"],
                output_modes=["text/plain"],
            )
            for name in settings.mcp_server_urls
        ],
    )
