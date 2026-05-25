from __future__ import annotations

import re
from typing import TypeAlias

from .config import settings

KeepAliveValue: TypeAlias = int | str


def ollama_keep_alive_value() -> KeepAliveValue:
    """Translate environment string settings to an Ollama API-compatible value."""
    raw = str(settings.ollama_keep_alive).strip()
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw
