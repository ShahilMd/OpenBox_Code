from __future__ import annotations

from collections.abc import AsyncGenerator

from agent.events import AgentEvent, AgentEventType
from client.llm_client import LLMClient
from client.response import EventType


class Agent:
    def __init__(self) -> None:
        self.client: LLMClient | None = None

    async def run(self, message: str):
        yield AgentEvent.agent_start(message)

        final_response: str | None = None
        async for event in self._agentic_loop(message):
            yield event

            if event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")

        yield AgentEvent.agent_end(final_response)

    async def _agentic_loop(self, message: str) -> AsyncGenerator[AgentEvent, None]:
        if self.client is None:
            raise RuntimeError(
                "Agent client is not initialized, use `async with Agent()`"
            )

        messages = [
            {
                "role": "user",
                "content": message,
            }
        ]

        response_text = ""
        async for event in self.client.chat_completion(messages, True):
            if event.type == EventType.TEXT_DELTA and event.text_delta:
                content = event.text_delta.content
                response_text += content
                yield AgentEvent.text_delta(content)
            elif event.type == EventType.ERROR:
                yield AgentEvent.agent_error(event.error or "Unknown error")

        if response_text:
            yield AgentEvent.text_complete(response_text)

    async def __aenter__(self) -> Agent:
        self.client = LLMClient()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        client = getattr(self, "client", None)
        if client:
            await client.close()
            self.client = None
