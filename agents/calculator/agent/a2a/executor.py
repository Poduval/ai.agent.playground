"""The executor turns an incoming A2A message into work and reports progress as a Task.

Task lifecycle used here: Task created -> WORKING -> artifact produced -> COMPLETED or FAILED.
"""

from a2a.helpers import (
    get_message_text,
    new_task_from_user_message,
    new_text_artifact_update_event,
    new_text_status_update_event,
)
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types.a2a_pb2 import TaskState

from agent.main import Agent


class ToolAgentExecutor(AgentExecutor):
    def __init__(self, agent: Agent | None = None):
        self._agent = agent  # built lazily so the card can be served without an LLM key

    async def _solve(self, text: str, session_id: str) -> str:
        self._agent = self._agent or Agent()
        return await self._agent.run(text, session_id=session_id)

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task_from_user_message(context.message)
        await event_queue.enqueue_event(task)  # A2A requires the Task to be emitted first
        await event_queue.enqueue_event(
            new_text_status_update_event(task_id=task.id, context_id=task.context_id, state=TaskState.TASK_STATE_WORKING, text="Working...")
        )
        try:
            answer = await self._solve(get_message_text(context.message), session_id=task.context_id)
            await event_queue.enqueue_event(
                new_text_artifact_update_event(task_id=task.id, context_id=task.context_id, name="answer", text=answer)
            )
            state, status = TaskState.TASK_STATE_COMPLETED, "Done."
        except Exception as exc:
            state, status = TaskState.TASK_STATE_FAILED, f"Failed: {exc}"
        await event_queue.enqueue_event(
            new_text_status_update_event(task_id=task.id, context_id=task.context_id, state=state, text=status)
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Cancellation is not supported.")
