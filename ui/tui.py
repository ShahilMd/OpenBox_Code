
from rich.console import Console
from rich.theme import Theme

AGENT_THEME = Theme(
)


_console: Console | None = None

def get_console() -> Console:
    global _console
    if _console is None:
        _console = Console(theme=AGENT_THEME, highlight=True)

    return _console



class TUI:

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or get_console()

    def strem_assistent_delta(self, content:str) -> None:
        self.console.print(content, end="", markup=False)