import asyncio
import sys

import click

from ui.theme import get_console as get_theme_console
from agent.agent import Agent
from agent.events import AgentEventType
from ui.tui import TUI, get_console

console = get_console()
error_console = get_theme_console(stderr=True)


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

        assistent_streaming = False
        final_response: str | None = None

        async for event in self.agent.run(message):
            if event.type == AgentEventType.TEXT_DELTA:
                content = event.data.get("content", "")
                if not assistent_streaming:
                    self.tui.begain_assistent()
                    assistent_streaming = True

                self.tui.strem_assistent_delta(content)

            elif event.type == AgentEventType.AGENT_ERROR:
                error = event.data.get("error", "Unknown error")
                error_console.print(
                    f"\nError: {error}",
                    style="status.error",
                    markup=False,
                    highlight=False,
                )
                click.echo("Please try again.", err=True)
                return None

            elif event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("response")
                if assistent_streaming:
                    self.tui.end_assistent()
                    assistent_streaming = False

        return final_response


@click.command()
@click.argument("prompt", required=False)
def main(prompt: str | None) -> None:
    cli = CLI()

    if prompt:
        result = asyncio.run(cli.run_single(prompt))

        if result is None:
            sys.exit(1)


main()
