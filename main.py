import asyncio
import sys

import click

from agent.agent import Agent
from agent.events import AgentEventType
from ui.tui import TUI, get_console

console = get_console()


class CLI:
    def __init__(self) -> None:
        self.agent: Agent | None = None
        self.tui = TUI(console)

    async def run_single(self, message: str) -> str | None:
        async with Agent() as agent:
            self.agent = agent
            return await self._process_message(message)

    async def _process_message(self, message: str) -> str | None:
        if not self.agent:
            return None

        response: str | None = None
        async for event in self.agent.run(message):
            if event.type == AgentEventType.TEXT_DELTA:
                content = event.data.get("content", "")
                self.tui.strem_assistent_delta(content)
            elif event.type == AgentEventType.AGENT_END:
                response = event.data.get("response")

        self.tui.strem_assistent_delta("\n")
        return response


@click.command()
@click.argument("prompt", required=False)
def main(prompt: str | None) -> None:
    cli = CLI()

    if prompt:
        result = asyncio.run(cli.run_single(prompt))
        if result is None:
            sys.exit(1)


main()
