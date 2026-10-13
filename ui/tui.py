
from rich.text import Text
from rich.rule import Rule
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
        self._assistent_running = False

    def begain_assistent(self) -> None:
        self.console.print()
        self.console.print(Rule(Text("Assistent is starting...", style="bold blue")))
        self._assistent_running = True

    def end_assistent(self) -> None:
        self.console.print()
        self._assistent_running = False

    def strem_assistent_delta(self, content:str) -> None:
        self.console.print(content, end="", markup=False)