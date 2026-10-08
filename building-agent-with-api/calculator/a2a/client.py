"""A2A client: discover an agent from its card, then send it a task with the bearer token."""

import httpx
from a2a.client import ClientConfig, create_client
from a2a.helpers import get_stream_response_text, new_text_message
from a2a.types import Role, SendMessageRequest

from calculator.config import get_settings


async def ask_agent(text: str, context_id: str | None = None) -> str:
    """Send `text` to the calculator agent and return its final answer."""
    settings = get_settings()
    headers = {"Authorization": f"Bearer {settings.a2a_bearer_token}"}
    async with httpx.AsyncClient(headers=headers, timeout=60) as http:
        client = await create_client(settings.a2a_url, ClientConfig(httpx_client=http, streaming=False))
        message = new_text_message(text=text, role=Role.ROLE_USER, context_id=context_id)
        answer = ""
        async for event in client.send_message(SendMessageRequest(message=message)):
            answer = get_stream_response_text(event) or answer  # keep the latest non-empty text
    if not answer:
        raise RuntimeError("The calculator agent returned no result.")
    return answer
