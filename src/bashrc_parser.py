"""Bashrc alias parsing — extracts aliases as shortcut items."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Union

from .parser import ShortcutItem, ParsedContent


def parse_bashrc(
    file_path: Union[str, Path],
    skip_sections: Optional[List[str]] = None,
    include_partial: bool = True,
) -> ParsedContent:
    """Parse a bashrc file and extract aliases as a flat list."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    items: List[ShortcutItem] = []

    for line in lines:
        line = line.rstrip()

        # Skip blank lines, exports, comments, and non-alias lines
        if not line.strip() or line.strip().startswith(("#", "export ")):
            continue

        alias_match = re.match(r"^alias\s+([\w][\w-]*)=(.+)$", line)
        if alias_match:
            name = alias_match.group(1)
            value = _strip_outer_quotes(alias_match.group(2))
            items.append(ShortcutItem(shortcut=name, description=value))

    return ParsedContent(items=items)


def _strip_outer_quotes(value: str) -> str:
    """Strip outer quotes from an alias value, handling escaped inner quotes."""
    value = value.strip()
    if len(value) >= 2:
        if (value[0] == '"' and value[-1] == '"') or (
            value[0] == "'" and value[-1] == "'"
        ):
            value = value[1:-1]
    value = value.replace('\\"', '"')
    return value
