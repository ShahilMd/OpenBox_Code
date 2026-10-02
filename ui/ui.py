"""OpenBox Code UI — compatibility façade.

The palette/theme lives in :mod:`ui.theme` and the widgets in
:mod:`ui.components`; this module re-exports the public API so existing
imports keep working::

    from ui.ui import AGENT_THEME, get_console
"""

from ui.components import *  # noqa: F403
from ui.theme import *  # noqa: F403
from ui.theme import AGENT_THEME, get_console  # explicit re-export

__all__ = ["AGENT_THEME", "get_console"]
