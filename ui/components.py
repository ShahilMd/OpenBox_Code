"""Reusable Rich renderables for the OpenBox Code terminal UI.

Everything here is style-agnostic: colours always come from the named styles
declared in :mod:`ui.theme`, so changing the theme restyles every widget.

Usage::

    from ui import banner, user_message, agent_message, AgentStream

    console = get_console()
    console.print(banner(model="anthropic/claude-sonnet-4"))
"""

from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterable, Mapping
from typing import Any

from rich import box
from rich.console import Console, ConsoleRenderable, Group
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ui.theme import (
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    BRAND_GRADIENT,
    CODE_THEME,
    get_console,
)

# --------------------------------------------------------------------------
# Block wordmark
# --------------------------------------------------------------------------
_GLYPH_ROWS = 5
_GLYPH_COLS = 5

_GLYPHS: dict[str, tuple[str, ...]] = {
    "O": (" ███ ", "█   █", "█   █", "█   █", " ███ "),
    "P": ("████ ", "█   █", "████ ", "█    ", "█    "),
    "E": ("█████", "█    ", "████ ", "█    ", "█████"),
    "N": ("█   █", "██  █", "█ █ █", "█  ██", "█   █"),
    "B": ("████ ", "█   █", "████ ", "█   █", "████ "),
    "X": ("█   █", " █ █ ", "  █  ", " █ █ ", "█   █"),
    "C": (" ████", "█    ", "█    ", "█    ", " ████"),
    "D": ("████ ", "█   █", "█   █", "█   █", "████ "),
    " ": ("     ", "     ", "     ", "     ", "     "),
}


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _mix(color_a: str, color_b: str, position: float) -> str:
    """Linearly blend two ``#rrggbb`` colours (``position`` is 0.0 - 1.0)."""
    rgb_a, rgb_b = _hex_to_rgb(color_a), _hex_to_rgb(color_b)
    mixed = [round(a + (b - a) * position) for a, b in zip(rgb_a, rgb_b, strict=True)]
    return "#{:02x}{:02x}{:02x}".format(*mixed)


def _gradient_at(stops: tuple[str, ...], position: float) -> str:
    """Sample a colour from a multi-stop gradient at ``position`` (0.0-1.0)."""
    if len(stops) < 2 or position <= 0:
        return stops[0]
    if position >= 1:
        return stops[-1]
    scaled = position * (len(stops) - 1)
    index = min(int(scaled), len(stops) - 2)
    return _mix(stops[index], stops[index + 1], scaled - index)


def gradient(text: str, stops: tuple[str, ...] = BRAND_GRADIENT) -> Text:
    """Render ``text`` with a left-to-right colour gradient."""
    rendered = Text()
    last = len(text) - 1
    for index, char in enumerate(text):
        position = 0.0 if last <= 0 else index / last
        rendered.append(char, style=_gradient_at(stops, position))
    return rendered


def wordmark(
    text: str = "OPENBOX",
    *,
    stops: tuple[str, ...] = BRAND_GRADIENT,
    indent: str = "  ",
) -> Text:
    """Build a 5-row block-letter wordmark painted with the brand gradient.

    Only letters available in :data:`_GLYPHS` are drawn as blocks; any other
    character falls back to a blank cell, keeping the grid intact.
    """
    letters = text.upper()
    rows = [
        " ".join(_GLYPHS.get(char, _GLYPHS[" "])[row] for char in letters)
        for row in range(_GLYPH_ROWS)
    ]
    width = max(len(row) for row in rows)

    art = Text(justify="left")
    for index, row in enumerate(rows):
        if index:
            art.append("\n")
        art.append(indent)
        art.append(gradient(row.ljust(width), stops))
    return art


def banner(
    *,
    model: str | None = None,
    workdir: str | None = None,
    version: str = APP_VERSION,
    show_env: bool = True,
) -> ConsoleRenderable:
    """The OpenBox Code start-up banner: wordmark, tagline and session meta."""
    heading = Text.assemble(
        ("  ", None),
        gradient("C O D E", (BRAND_GRADIENT[-1], *BRAND_GRADIENT)),
        "  ",
        (APP_TAGLINE, "openbox.tagline"),
    )

    meta = Table(box=None, show_header=False, show_edge=False, pad_edge=False)
    meta.add_column(style="openbox.meta_key", justify="left", no_wrap=True)
    meta.add_column(style="openbox.meta_value", justify="left")
    meta.add_row("model", model or "unset")
    if workdir:
        meta.add_row("path", _shorten_path(workdir))
    if show_env:
        python_version = sys.version_info
        meta.add_row(
            "runtime",
            f"python {python_version.major}"
            f".{python_version.minor}"
            f".{python_version.micro}",
        )

    return Group(
        Text(),
        wordmark(),
        heading,
        Text(),
        Rule(style="openbox.rule"),
        meta,
        Rule(style="openbox.rule"),
        Text.assemble(
            ("  ", None),
            (f"{APP_NAME} v{version}", "openbox.version"),
            ("  ·  ", "openbox.rule"),
            ("ctrl+c to interrupt", "openbox.version"),
        ),
        Text(),
    )


def _shorten_path(path: str, *, keep: int = 2) -> str:
    """Collapse ``/home/user/projects/app/src/x.py`` to ``…/app/src/x.py``."""
    expanded = os.path.expanduser(path)
    prefix = os.sep if expanded.startswith(os.sep) else ""
    parts = [part for part in expanded.split(os.sep) if part]
    if len(parts) <= keep:
        return prefix + os.sep.join(parts)
    return f"…{os.sep}{os.sep.join(parts[-keep:])}"


def rule(title: str = "", *, style: str = "openbox.rule") -> ConsoleRenderable:
    """A themed horizontal rule with an optional label."""
    return Rule(title=title or None, style=style, characters="─")


# --------------------------------------------------------------------------
# Chat blocks
# --------------------------------------------------------------------------
PROMPT_GLYPH = "❯"
"""Drawn in front of everything the human types."""

AGENT_GLYPH = "●"
"""Drawn in front of everything the agent says."""


def user_message(text: str) -> ConsoleRenderable:
    """Render a user turn as a ``❯`` prompt with aligned continuation lines."""
    lines = text.rstrip("\n").splitlines() or [""]
    body = Text()
    for index, line in enumerate(lines):
        glyph = f"{PROMPT_GLYPH} " if index == 0 else "  "
        body.append(f"  {glyph}", style="user.prompt")
        body.append(line, style="user.input")
        if index < len(lines) - 1:
            body.append("\n")
    return body


def agent_message(
    text: str,
    *,
    title: str = "agent",
    markdown: bool = True,
) -> ConsoleRenderable:
    """Render a finished agent turn inside a bordered bubble."""
    body: ConsoleRenderable = (
        Markdown(text, code_theme=CODE_THEME)
        if markdown
        else Text(text, style="agent.text")
    )
    return Panel(
        body,
        title=Text.assemble((f"{AGENT_GLYPH} ", "agent.label"), (title, "agent.label")),
        title_align="left",
        box=box.ROUNDED,
        border_style="panel.border",
        padding=(0, 1),
        expand=False,
    )


def reasoning(text: str) -> ConsoleRenderable:
    """Render planning / chain-of-thought text in a muted, italic block."""
    return Padding(Text(text, style="agent.reasoning"), (0, 0, 0, 3))


def code_block(
    code: str,
    language: str = "text",
    *,
    filename: str | None = None,
    line_numbers: bool = True,
    background: str | None = None,
) -> ConsoleRenderable:
    """Render a syntax-highlighted snippet on the sunken background."""
    syntax = Syntax(
        code.rstrip("\n"),
        language,
        theme=CODE_THEME,
        line_numbers=line_numbers,
        background_color=background or "black",
        word_wrap=True,
    )
    return Panel(
        syntax,
        title=filename,
        title_align="left",
        box=box.SQUARE,
        border_style="panel.border",
        padding=(0, 1),
    )


class AgentStream:
    """Write streamed deltas straight to the terminal, keeping the raw text.

    ``write`` is markup-safe: partial JSON or stray square brackets coming
    from the model never crash the renderer.

    ::

        with AgentStream() as stream:
            async for delta in agent.tokens():
                stream.write(delta)
        print(stream.text)
    """

    def __init__(
        self,
        console: Console | None = None,
        *,
        style: str = "agent.stream",
        indent: str = "  ",
    ) -> None:
        self.console = console or get_console()
        self.style = style
        self.indent = indent
        self._parts: list[str] = []
        self._at_line_start = True

    @property
    def text(self) -> str:
        """Everything written so far."""
        return "".join(self._parts)

    def write(self, delta: str) -> None:
        if not delta:
            return
        self._parts.append(delta)
        for index, chunk in enumerate(delta.split("\n")):
            if index:
                self.console.print("")
                self._at_line_start = True
            if not chunk:
                continue
            prefix = self.indent if self._at_line_start else ""
            self._at_line_start = False
            self.console.print(
                f"{prefix}{chunk}",
                style=self.style,
                end="",
                markup=False,
                highlight=False,
            )

    def finish(self) -> str:
        """Terminate the open line and return the accumulated text."""
        if not self._at_line_start:
            self.console.print("")
        self._at_line_start = True
        return self.text

    def __enter__(self) -> AgentStream:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.finish()


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------
TOOL_GLYPH = "⚙"
RESULT_GLYPH = "↳"


def _clip(text: str, width: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else f"{text[: width - 1]}…"


def tool_call(
    name: str,
    args: Mapping[str, Any] | str | None = None,
    *,
    console: Console | None = None,
) -> None:
    """Print a tool invocation, e.g. ``⚙ read_file  path=src/app.tsx``."""
    console = console or get_console()
    if isinstance(args, str):
        summary = args
    elif args:
        summary = "  ".join(f"{key}={value}" for key, value in args.items())
    else:
        summary = ""
    line = Text.assemble(
        ("  ", None),
        (TOOL_GLYPH, "tool.glyph"),
        (" ", None),
        (name, "tool.name"),
    )
    if summary:
        line.append("  ", None)
        line.append(_clip(summary, 96), style="tool.args")
    console.print(line)


def tool_result(
    summary: str,
    *,
    ok: bool = True,
    duration: float | None = None,
    console: Console | None = None,
) -> None:
    """Print the outcome of a tool call underneath its ``tool_call`` line."""
    console = console or get_console()
    line = Text.assemble(
        ("  ", None),
        (RESULT_GLYPH, "tool.result"),
        (" ", None),
        ("ok" if ok else "failed", "tool.ok" if ok else "tool.fail"),
        ("  ", None),
        (_clip(summary, 96), "tool.result"),
    )
    if duration is not None:
        line.append(f"  {duration:.2f}s", style="telemetry.duration")
    console.print(line)


# --------------------------------------------------------------------------
# Notices
# --------------------------------------------------------------------------
_LEVELS: dict[str, tuple[str, str]] = {
    "info": ("status.info", "ℹ"),
    "ok": ("status.ok", "✔"),
    "warn": ("status.warn", "⚠"),
    "error": ("status.error", "✖"),
}


def notice(
    level: str,
    text: str,
    *,
    console: Console | None = None,
) -> None:
    """Print a one-line iconified status message (info/ok/warn/error)."""
    style, glyph = _LEVELS.get(level, _LEVELS["info"])
    console = console or get_console()
    console.print(
        Text.assemble(
            ("  ", None),
            (glyph, style),
            (" ", None),
            (text, "openbox.meta_value"),
        )
    )


def error_panel(
    error: object,
    *,
    hint: str | None = None,
    details: Iterable[str] | None = None,
    console: Console | None = None,
) -> None:
    """Print a failure inside a red bordered panel with an optional hint."""
    console = console or get_console()
    body = Text(str(error), style="status.error")
    for line in details or ():
        body.append("\n")
        body.append(_clip(line, 200), style="tool.result")
    if hint:
        body.append(f"\n\nhint: {hint}", style="status.info")
    console.print(
        Panel(
            body,
            title="✖ error",
            title_align="left",
            box=box.ROUNDED,
            border_style="status.error",
            padding=(0, 1),
            expand=False,
        )
    )


# --------------------------------------------------------------------------
# Telemetry
# --------------------------------------------------------------------------
def _usage_int(usage: Any, *keys: str) -> int:
    """Read an int from a dataclass, plain object or mapping without importing."""
    for key in keys:
        if isinstance(usage, Mapping):
            value = usage.get(key)
        else:
            value = getattr(usage, key, None)
        if isinstance(value, int):
            return value
    return 0


def usage_line(
    usage: Any | None = None,
    *,
    model: str | None = None,
    duration: float | None = None,
    cost: float | None = None,
) -> Text:
    """Build the compact footer shown after a turn.

    ``usage`` may be a ``TokenUsage`` instance, a plain object or a dict;
    anything unrecognised is simply skipped.
    """
    parts = Text()

    def add(text: str, style: str) -> None:
        if parts.plain:
            parts.append("  ·  ", style="telemetry.label")
        parts.append(text, style=style)

    if model:
        add(model, "telemetry.model")
    if usage is not None:
        prompt = _usage_int(usage, "prompt_tokens", "input_tokens")
        completion = _usage_int(usage, "completion_tokens", "output_tokens")
        total = _usage_int(usage, "total_tokens") or prompt + completion
        if total:
            add(
                f"↑{prompt:,} ↓{completion:,} = {total:,} tok",
                "telemetry.tokens",
            )
    if duration is not None:
        add(f"{duration:.1f}s", "telemetry.duration")
    if cost is not None:
        add(f"${cost:.4f}", "telemetry.cost")
    return Text.assemble(("  ", None), parts) if parts.plain else parts


def status(
    message: str,
    *,
    console: Console | None = None,
    spinner: str = "dots12",
):
    """A themed spinner for long-running work::

    with status("thinking…"):
        await agent.turn()
    """
    console = console or get_console()
    return console.status(
        Text.assemble(("  ", None), (message, "status.info")),
        spinner=spinner,
    )


# --------------------------------------------------------------------------
# Agent event bridge
# --------------------------------------------------------------------------
def _event_name(event: Any) -> str:
    event_type = getattr(event, "type", None)
    name = getattr(event_type, "name", None)
    if isinstance(name, str):
        return name.upper()
    return str(event_type).upper()


class EventRenderer:
    """Translate agent events into themed terminal output.

    Keeps a single :class:`AgentStream` alive across ``TEXT_DELTA`` events and
    closes the line as soon as the turn ends, so streaming never interleaves
    with tool or status output.

    ::

        renderer = EventRenderer()
        async for event in agent.run(prompt):
            renderer.render(event)
        renderer.close()
    """

    def __init__(self, console: Console | None = None, *, indent: str = "  ") -> None:
        self.console = console or get_console()
        self.indent = indent
        self._stream: AgentStream | None = None
        self.started = time.perf_counter()

    def render(self, event: Any) -> None:
        name = _event_name(event)
        data = getattr(event, "data", None)
        data = data if isinstance(data, Mapping) else {}

        if name == "AGENT_START":
            self.close()
            self.started = time.perf_counter()
            self.console.print(
                Text.assemble(
                    ("  ", None),
                    ("▶ ", "agent.start"),
                    (str(data.get("message", "")), "agent.label"),
                )
            )
        elif name == "TEXT_DELTA":
            if self._stream is None:
                self._stream = AgentStream(self.console, indent=self.indent)
            self._stream.write(str(data.get("content", "")))
        elif name == "TEXT_COMPLETE":
            final = str(data.get("content", ""))
            if self._stream is not None and self._stream.text == final:
                self._stream.finish()
            elif final:
                self.close()
                self.console.print(
                    Text.assemble((self.indent, None), (final, "agent.text"))
                )
            self._stream = None
        elif name == "AGENT_ERROR":
            self.close()
            details = data.get("details")
            error_panel(
                data.get("error", "unknown error"),
                details=[str(details)] if details else None,
                console=self.console,
            )
        elif name == "AGENT_END":
            self.close()
            self.console.print(
                usage_line(
                    data.get("usage"),
                    duration=time.perf_counter() - self.started,
                )
            )

    def close(self) -> None:
        """Flush any half-finished streamed line."""
        if self._stream is not None:
            self._stream.finish()
            self._stream = None
