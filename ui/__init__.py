"""OpenBox Code terminal UI.

Theme + widgets for the agent CLI:

* :mod:`ui.theme`     — palette, Rich ``Theme``, themed console factory
* :mod:`ui.components` — banner, chat blocks, tool rows, telemetry footer

``from ui.ui import ...`` and ``from ui import ...`` both work.
"""

from ui.components import (
    AGENT_GLYPH,
    PROMPT_GLYPH,
    AgentStream,
    EventRenderer,
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
    wordmark,
)
from ui.theme import (
    AGENT_THEME,
    APP_COMMAND,
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    BRAND_GRADIENT,
    PALETTE,
    STYLES,
    get_console,
)

__all__ = [
    "AGENT_GLYPH",
    "AGENT_THEME",
    "APP_COMMAND",
    "APP_NAME",
    "APP_TAGLINE",
    "APP_VERSION",
    "BRAND_GRADIENT",
    "PALETTE",
    "PROMPT_GLYPH",
    "STYLES",
    "AgentStream",
    "EventRenderer",
    "agent_message",
    "banner",
    "code_block",
    "error_panel",
    "get_console",
    "notice",
    "reasoning",
    "rule",
    "status",
    "tool_call",
    "tool_result",
    "usage_line",
    "user_message",
    "wordmark",
]
