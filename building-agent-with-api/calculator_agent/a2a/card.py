"""The Agent Card: the public "business card" other agents read to learn what this agent does.

Served at /.well-known/agent-card.json (no auth). It declares skills, supported modes
and the security scheme callers must use for the JSON-RPC endpoint.
"""

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.types.a2a_pb2 import HTTPAuthSecurityScheme, SecurityRequirement, SecurityScheme, StringList

from calculator_agent import __version__
from calculator_agent.config import Settings, get_settings


def build_agent_card(settings: Settings | None = None) -> AgentCard:
    settings = settings or get_settings()
    return AgentCard(
        name="Calculator Agent",
        description="Does arithmetic (add, subtract, multiply, divide) by calling MCP tools.",
        version=__version__,
        documentation_url="https://github.com/Poduval/ai.agent.playground",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain", "application/json"],
        capabilities=AgentCapabilities(streaming=False),
        supported_interfaces=[AgentInterface(protocol_binding="JSONRPC", protocol_version="1.0", url=settings.a2a_url)],
        security_schemes={
            "bearer": SecurityScheme(http_auth_security_scheme=HTTPAuthSecurityScheme(scheme="Bearer", description="Static bearer token"))
        },
        security_requirements=[SecurityRequirement(schemes={"bearer": StringList()})],
        skills=[
            AgentSkill(
                id="structured-arithmetic",
                name="Structured arithmetic",
                description="Send JSON with operation, a and b; the agent calls the MCP tool directly (no LLM).",
                tags=["math", "mcp", "deterministic"],
                examples=['{"operation": "divide", "a": 84, "b": 2}'],
                input_modes=["application/json", "text/plain"],
                output_modes=["application/json"],
            ),
            AgentSkill(
                id="natural-language-math",
                name="Natural-language math",
                description="Ask in plain English; an LLM picks MCP tools, and conversation memory is kept per context.",
                tags=["math", "llm", "memory"],
                examples=["What is 6 multiplied by 7?", "Now divide that by 2"],
                input_modes=["text/plain"],
                output_modes=["text/plain"],
            ),
        ],
    )
