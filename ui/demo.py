"""Live preview of the OpenBox Code theme.

Run it to see every widget rendered with real content::

    python -m ui.demo
    python -m ui.demo --width 100
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Iterator

from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ui.components import (
    AgentStream,
    agent_message,
    banner,
    code_block,
    error_panel,
    notice,
    reasoning,
    rule,
    status,
    tool_call,
    tool_result,
    usage_line,
    user_message,
)
from ui.theme import APP_NAME, PALETTE, STYLES, get_console

SAMPLE_ANSWER = """\
### Here is the plan

1. Wrap the streaming loop in `try/except` so a dropped socket becomes an
   `AGENT_ERROR` event instead of a traceback.
2. Yield `agent_end` in a `finally` block so usage is always reported.

```python
async for event in self._agentic_loop():
    if event.type == AgentEventType.TEXT_DELTA:
        yield event
```

> Costs are reported per turn; see `client/response.py` for the usage model.
"""

SAMPLE_PATCH = """\
@@ -18,7 +18,10 @@ class Agent:
     async def run(self, message: str):
         yield AgentEvent.agent_start(message)
-        async for event in self._agentic_loop():
-            yield event
+        try:
+            async for event in self._agentic_loop():
+                yield event
+        finally:
+            yield AgentEvent.agent_end(final_response)
"""

FAKE_DELTAS = [
    "Streaming ",
    "deltas ",
    "stay markup-safe ",
    "even when the model emits ",
    'json like {"tools": ["bash"]}',
    " mid-token.",
]


def fake_stream(*, chunk_delay: float = 0.02) -> Iterator[str]:
    yield from FAKE_DELTAS
    time.sleep(chunk_delay)


def palette_table() -> Panel:
    """Swatch every palette colour so it can be eyeballed in the terminal."""
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="table.header",
        border_style="panel.border",
        title="palette",
        title_style="italic",
        expand=True,
    )
    table.add_column("token", style="openbox.meta_key", no_wrap=True)
    table.add_column("swatch", width=8)
    table.add_column("hex", style="openbox.meta_value")
    table.add_column("used for", style="openbox.meta_value")

    roles = {
        "violet": "brand · agent · keywords",
        "cyan": "user · tokens · links",
        "teal": "runtime · strings · finished",
        "mint": "success · diff added",
        "amber": "tools · cost · warnings",
        "coral": "errors · diff removed",
        "pink": "pulse · json bool",
        "steel": "neutral data · args",
        "muted": "secondary text",
        "faint": "gutters · placeholders",
        "border": "panels · rules",
        "bg_raised": "panels",
        "bg_sunken": "code blocks",
    }
    for name, hex_color in PALETTE.items():
        table.add_row(
            name,
            Text("██████", style=f"on {hex_color}"),
            hex_color,
            roles.get(name, ""),
        )
    return Panel(
        table,
        border_style="panel.border",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def style_listing(limit: int = 14) -> Panel:
    """Show the first ``limit`` named styles with a live sample of each."""
    table = Table(box=None, show_header=False, expand=True)
    table.add_column("style", style="openbox.meta_key", ratio=2)
    table.add_column("sample", ratio=3)
    for name, style in list(STYLES.items())[:limit]:
        table.add_row(name, Text(f"the quick brown fox · 1337 · {name}", style=style))
    return Panel(
        table,
        title="named styles",
        title_align="left",
        border_style="panel.border",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def main(*, width: int | None = None) -> None:
    """Render every widget once so the theme can be reviewed in one screen."""
    console = get_console(**({"width": width} if width else {}))
    model = "nex-agi/nex-n2.5-mini:free"

    console.print(banner(model=model, workdir="~/coding/Claude_Clone"))

    console.print(
        user_message("Refactor the agent loop so tool errors\nnever kill the run")
    )
    console.print()
    console.print(
        reasoning("planning: read agent.py → guard the stream → re-emit agent_end")
    )
    console.print()

    with status("thinking…", console=console):
        time.sleep(0.5)

    tool_call("read_file", {"path": "agent/agent.py", "offset": 18}, console=console)
    tool_result("41 lines", ok=True, duration=0.12, console=console)
    tool_call("edit_file", "agent/agent.py: wrap stream in try/except", console=console)
    tool_result("patch applied", ok=True, duration=0.31, console=console)
    tool_call("run_tests", {"cmd": "pytest -q"}, console=console)
    tool_result("2 failed, 18 passed", ok=False, duration=4.87, console=console)
    console.print()

    with AgentStream(console) as stream:
        for delta in fake_stream():
            stream.write(delta)

    console.print()
    console.print(agent_message(SAMPLE_ANSWER, title="agent"))
    console.print()
    console.print(code_block(SAMPLE_PATCH, "diff", filename="agent/agent.py"))
    console.print()

    notice("info", "4 tools available · bash, read_file, edit_file", console=console)
    notice("ok", "context compacted — 12k tokens reclaimed", console=console)
    notice("warn", "model returned an empty tool argument list", console=console)
    console.print()
    error_panel(
        "ConnectionResetError: peer closed connection mid-stream",
        details=["openai.APIError: stream aborted after 3 deltas"],
        hint="retry the turn — partial output is kept in the transcript",
        console=console,
    )
    console.print()
    console.print(
        usage_line(
            {
                "prompt_tokens": 8128,
                "completion_tokens": 612,
                "total_tokens": 8740,
            },
            model=model,
            duration=6.4,
            cost=0.0031,
        )
    )

    console.print()
    console.print(rule("theme reference"))
    console.print(palette_table())
    console.print(style_listing())
    console.print(
        Panel(
            Markdown(
                "# h1 heading\n\n## h2 heading\n\n- bullets use the theme\n"
                "1. numbered items too"
            ),
            title="markdown and reprs inherit the theme",
            title_align="left",
            box=box.ROUNDED,
            border_style="panel.border",
            padding=(0, 1),
        )
    )
    console.print(
        Text.assemble(
            ("  ", None),
            ("repr → ", "telemetry.label"),
            ("True", "repr.bool_true"),
            (", ", ""),
            ("None", "repr.none"),
            (", ", ""),
            ("42", "repr.number"),
            (", ", ""),
            ('"openbox"', "repr.str"),
        )
    )
    console.print()
    notice("ok", f"{APP_NAME} theme preview complete", console=console)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ui.demo", description="OpenBox Code theme preview"
    )
    parser.add_argument("--width", type=int, default=None, help="force console width")
    args = parser.parse_args()
    main(width=args.width)
