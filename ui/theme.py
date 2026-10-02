"""Palette and Rich theme for the OpenBox Code terminal UI.

Every colour the UI uses is declared once in this module.  Components never
hard-code colours, they use the *named styles* registered in ``AGENT_THEME``,
so the whole app can be re-skinned by editing this file only.

Usage::

    from ui import AGENT_THEME, get_console

    console = get_console()          # themed console (singleton friendly)
    console.print("hello", style="agent.text")
"""

from __future__ import annotations

import os

from rich.console import Console
from rich.theme import Theme

# --------------------------------------------------------------------------
# Brand identity
# --------------------------------------------------------------------------
APP_NAME = "OpenBox Code"
APP_SLUG = "openbox"
APP_COMMAND = "openbox"
APP_VERSION = "0.1.0"
APP_TAGLINE = "agentic coding in your terminal"

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
BG = "#0a0e17"  # page background
BG_RAISED = "#121a2b"  # panels / cards
BG_SUNKEN = "#070a11"  # code blocks, diffs, insets
FG = "#dce3f0"  # body copy
FG_HEADING = "#f2f5fb"  # titles, headings
MUTED = "#7c89a6"  # secondary text
FAINT = "#4c5a75"  # de-emphasised text, gutters
BORDER = "#223050"  # default borders / rules
BORDER_ACTIVE = "#3b4f7a"  # focused borders

VIOLET = "#a78bfa"  # primary brand accent
INDIGO = "#818cf8"
CYAN = "#22d3ee"  # secondary brand accent (user side)
TEAL = "#2dd4bf"
MINT = "#4ade80"  # success / added
AMBER = "#fbbf24"  # warning / running tools
CORAL = "#fb7185"  # error / removed
PINK = "#f472b6"  # tool noise / debug
STEEL = "#94a3b8"  # neutral data

BRAND_GRADIENT: tuple[str, ...] = (VIOLET, INDIGO, CYAN, TEAL)
"""Colours interpolated across the wordmark."""

CODE_THEME = "monokai"
"""Pygments style used for code blocks and ``rich.syntax.Syntax``.

Code highlighting is driven by pygments, *not* by the Rich theme, so this is
the knob to change when the sample colours in ``python -m ui.demo`` feel off.
"""

PALETTE: dict[str, str] = {
    "bg": BG,
    "bg_raised": BG_RAISED,
    "bg_sunken": BG_SUNKEN,
    "fg": FG,
    "fg_heading": FG_HEADING,
    "muted": MUTED,
    "faint": FAINT,
    "border": BORDER,
    "border_active": BORDER_ACTIVE,
    "violet": VIOLET,
    "indigo": INDIGO,
    "cyan": CYAN,
    "teal": TEAL,
    "mint": MINT,
    "amber": AMBER,
    "coral": CORAL,
    "pink": PINK,
    "steel": STEEL,
}

# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------
STYLES: dict[str, str] = {
    # --- brand -----------------------------------------------------------
    "openbox.brand": f"bold {VIOLET}",
    "openbox.brand_alt": f"bold {CYAN}",
    "openbox.tagline": f"italic {MUTED}",
    "openbox.version": f"dim {FAINT}",
    "openbox.rule": f"{BORDER}",
    "openbox.meta_key": f"bold {STEEL}",
    "openbox.meta_value": MUTED,
    # --- chat: user side ---------------------------------------------------
    "user.prompt": f"bold {CYAN}",
    "user.label": f"bold {CYAN} on {BG_RAISED}",
    "user.input": FG_HEADING,
    "user.placeholder": f"italic {FAINT}",
    "user.continuation": FAINT,
    # --- chat: agent side --------------------------------------------------
    "agent.label": f"bold {VIOLET}",
    "agent.text": FG,
    "agent.stream": FG,
    "agent.reasoning": f"italic {MUTED}",
    "agent.cursor": f"bold reverse {VIOLET}",
    "agent.start": f"bold {TEAL}",
    "agent.end": f"bold {INDIGO}",
    # --- tools -------------------------------------------------------------
    "tool.glyph": f"bold {AMBER}",
    "tool.name": f"bold {AMBER}",
    "tool.args": STEEL,
    "tool.result": MUTED,
    "tool.pending": f"dim {MUTED}",
    "tool.ok": f"bold {MINT}",
    "tool.fail": f"bold {CORAL}",
    # --- semantic states ---------------------------------------------------
    "status.ok": f"bold {MINT}",
    "status.warn": f"bold {AMBER}",
    "status.error": f"bold {CORAL}",
    "status.info": f"bold {CYAN}",
    "status.idle": f"dim {FAINT}",
    "diff.added": f"{MINT} on #0d1f18",
    "diff.removed": f"{CORAL} on #22111a",
    "diff.context": MUTED,
    "diff.header": f"bold {STEEL}",
    # --- telemetry / footer ------------------------------------------------
    "telemetry.label": FAINT,
    "telemetry.tokens": f"bold {CYAN}",
    "telemetry.cost": f"bold {AMBER}",
    "telemetry.duration": f"bold {TEAL}",
    "telemetry.model": f"bold {VIOLET}",
    "token.input": f"{CYAN}",
    "token.output": f"{AMBER}",
    "token.total": f"bold {FG}",
    # --- generic widgets ---------------------------------------------------
    "badge.brand": f"bold white on {VIOLET}",
    "badge.user": f"bold {BG} on {CYAN}",
    "badge.agent": f"bold {BG} on {VIOLET}",
    "badge.tool": f"bold {BG} on {AMBER}",
    "badge.error": f"bold white on {CORAL}",
    "spinner": f"bold {VIOLET}",
    "list.bullet": VIOLET,
    "link": f"underline {CYAN}",
}

# --------------------------------------------------------------------------
# Overrides of Rich's own named styles — makes Markdown, tracebacks, JSON,
# progress bars and reprs match the OpenBox look for free.
# --------------------------------------------------------------------------
STYLES.update(
    {
        # panels, boxes, rules
        "panel.border": BORDER,
        "panel.title": f"bold {VIOLET}",
        "rule": f"{BORDER_ACTIVE}",
        "rule.line": BORDER,
        "rule.text": f"italic {MUTED}",
        # tables
        "table.header": f"bold {FG_HEADING}",
        "table.title": f"italic {VIOLET}",
        # trees (file trees, tool call graphs)
        "tree": BORDER_ACTIVE,
        # progress bars
        "progress.description": f"{STEEL}",
        "progress.percentage": f"bold {CYAN}",
        "progress.remaining": FAINT,
        "bar.back": BG_RAISED,
        "bar.complete": VIOLET,
        "bar.finished": TEAL,
        "bar.pulse": PINK,
        # spinners / status
        "spinner": VIOLET,
        # input widgets
        "input": FG,
        "input.cursor": f"reverse {CYAN}",
        "input.selection": f"{FG} on {BORDER}",
        # markdown
        "markdown.h1": f"bold {FG_HEADING}",
        "markdown.h2": f"bold {VIOLET}",
        "markdown.h3": f"bold {INDIGO}",
        "markdown.h4": f"bold {CYAN}",
        "markdown.h5": f"bold {TEAL}",
        "markdown.h6": f"dim {MUTED}",
        "markdown.block_quote": f"italic {MUTED}",
        "markdown.code": f"{AMBER}",
        "markdown.item.bullet": VIOLET,
        "markdown.item.number": CYAN,
        "markdown.link": f"underline {CYAN}",
        "markdown.link_url": f"underline {STEEL}",
        "markdown.hr": BORDER,
        # syntax highlighting is driven by pygments (see CODE_THEME below),
        # only the line-number gutter comes from the console theme.
        "syntax.number": FAINT,
        # reprs
        "repr.number": f"bold {AMBER}",
        "repr.str": f"{TEAL}",
        "repr.bool_true": f"bold {MINT}",
        "repr.bool_false": f"bold {CORAL}",
        "repr.none": f"italic {MUTED}",
        "repr.url": f"underline {CYAN}",
        "repr.ellipsis": MUTED,
        # json
        "json.key": f"bold {CYAN}",
        "json.str": f"{TEAL}",
        "json.number": f"bold {AMBER}",
        "json.null": f"italic {MUTED}",
        "json.bool": f"bold {PINK}",
        # tracebacks & logging
        "traceback.border": CORAL,
        "traceback.text": FG,
        "traceback.title": f"bold {CORAL}",
        "traceback.exc_type": f"bold {CORAL}",
        "traceback.exc_value": FG,
        "traceback.path": FAINT,
        "logging.level.debug": f"dim {MUTED}",
        "logging.level.info": f"{CYAN}",
        "logging.level.warning": f"bold {AMBER}",
        "logging.level.error": f"bold {CORAL}",
        "logging.level.critical": f"bold white on {CORAL}",
    }
)

AGENT_THEME = Theme(STYLES)
"""The OpenBox Code Rich theme."""

_console: Console | None = None


def get_console(**kwargs: object) -> Console:
    """Return the shared themed :class:`~rich.console.Console`.

    Keyword arguments are forwarded to :class:`~rich.console.Console` and
    override the defaults, e.g. ``get_console(width=120, force_terminal=True)``.
    Set ``NO_COLOR`` or ``TERM=dumb`` in the environment for a plain, unstyled
    console (handy for pipes and CI logs).
    """
    global _console

    plain = bool(os.environ.get("NO_COLOR")) or os.environ.get("TERM") == "dumb"
    defaults: dict[str, object] = {
        "theme": AGENT_THEME,
        "color_system": "standard" if plain else "auto",
        "highlight": True,
    }
    if plain:
        defaults["no_color"] = True

    if kwargs:
        # Explicit options asked for: build a throwaway console so the shared
        # singleton stays untouched for everyone else.
        defaults.update(kwargs)
        return Console(**defaults)  # type: ignore[arg-type]

    if _console is None:
        _console = Console(**defaults)  # type: ignore[arg-type]
    return _console


__all__ = [
    "AGENT_THEME",
    "APP_COMMAND",
    "APP_NAME",
    "APP_SLUG",
    "APP_TAGLINE",
    "APP_VERSION",
    "BRAND_GRADIENT",
    "CODE_THEME",
    "PALETTE",
    "STYLES",
    "get_console",
]
