"""Markdown parsing and filtering for shortcuts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class ShortcutItem:
    shortcut: str
    description: str


@dataclass
class HeaderItem:
    level: int  # 2, 3, 4, or 5
    text: str


@dataclass
class ParsedContent:
    items: List[Union[HeaderItem, ShortcutItem]]


def parse_markdown(
    file_path: Union[str, Path],
    skip_sections: Optional[List[str]] = None,
    include_partial: bool = True,
) -> ParsedContent:
    """Parse markdown file and extract shortcuts.

    Args:
        file_path: Path to the markdown file
        skip_sections: List of section headers to skip (case-insensitive)
        include_partial: Whether to include [-] partial checkbox items

    Returns:
        ParsedContent with headers and shortcut items
    """
    skip_sections = [s.lower() for s in (skip_sections or [])]

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    items: List[Union[HeaderItem, ShortcutItem]] = []
    current_skip_level: Optional[int] = None  # Track if we're in a skipped section

    for line in lines:
        line = line.rstrip()

        # Check for headers
        header_match = re.match(r'^(#{2,5})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            header_text = header_match.group(2).strip()

            # Check if this header should be skipped
            header_clean = _clean_header_text(header_text).lower()

            if any(skip in header_clean for skip in skip_sections):
                current_skip_level = level
                continue

            # If we encounter a header at same or higher level, stop skipping
            if current_skip_level is not None and level <= current_skip_level:
                current_skip_level = None

            # Skip if we're in a skipped section
            if current_skip_level is not None:
                continue

            items.append(HeaderItem(level=level, text=_clean_header_text(header_text)))
            continue

        # Skip if we're in a skipped section
        if current_skip_level is not None:
            continue

        # Check for checkbox items
        # Patterns: - [ ], - [x], - [-], * [ ], * [x], * [-]
        checkbox_match = re.match(r'^[-*]\s*\[([ x\-])\]\s*(.+)$', line)

        if checkbox_match:
            state = checkbox_match.group(1)
            content = checkbox_match.group(2)

            # Skip checked items
            if state == 'x':
                continue

            # Skip partial items if not included
            if state == '-' and not include_partial:
                continue

            shortcut, description = _extract_shortcut_description(content)
            if shortcut:
                items.append(ShortcutItem(shortcut=shortcut, description=description))
            continue

        # Check for non-checkbox lines that might contain shortcuts
        # Lines starting with text (not header, not checkbox)
        if line.strip() and not line.startswith('#') and not line.startswith('---'):
            # Skip links and canvas references
            if line.strip().startswith('[[') or line.strip().startswith('['):
                continue

            shortcut, description = _extract_shortcut_description(line)
            if shortcut:
                items.append(ShortcutItem(shortcut=shortcut, description=description))

    return ParsedContent(items=items)


def _clean_header_text(text: str) -> str:
    """Clean header text by removing markdown syntax and emojis."""
    # Remove links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove wiki links [[text]]
    text = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', text)
    # Remove emojis (common unicode ranges)
    text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
    # Remove common task emojis
    text = re.sub(r'[✅🔺⏫🔽❌⬆️⬇️]', '', text)
    return text.strip()


def _extract_shortcut_description(content: str) -> tuple[str, str]:
    """Extract shortcut and description from content.

    Looks for:
    1. Bold text (**shortcut**) as the shortcut
    2. If no bold, looks for pattern before dash/hyphen

    Returns:
        Tuple of (shortcut, description)
    """
    # Clean the content first
    content = _clean_line(content)

    # Look for bold shortcuts: **shortcut**
    bold_match = re.search(r'\*\*([^*]+)\*\*', content)

    if bold_match:
        shortcut = bold_match.group(1).strip()

        # Get description: everything after the first bold section
        # Handle cases like "**alt + z** or **alt + c** - description"
        rest = content[bold_match.end():].strip()

        # Check for additional bold shortcuts (like "or **alt + c**")
        additional_shortcuts = re.findall(r'\*\*([^*]+)\*\*', rest)

        # Remove the bold markers and clean up
        description = re.sub(r'\*\*[^*]+\*\*', '', rest).strip()

        # Clean up leading "or", "-", etc.
        description = re.sub(r'^(?:or\s+)?[-–—]\s*', '', description).strip()
        description = re.sub(r'^[-–—]\s*', '', description).strip()

        # If there were additional shortcuts, add them to description
        if additional_shortcuts:
            alt_text = " or ".join(additional_shortcuts)
            if description:
                description = f"(also {alt_text}) {description}"
            else:
                description = f"or {alt_text}"

        return shortcut, description

    # No bold text - try to find shortcut pattern before dash
    # Pattern: "ctrl + something - description"
    dash_match = re.match(r'^([^-–—]+?)[-–—]\s*(.+)$', content)

    if dash_match:
        potential_shortcut = dash_match.group(1).strip()
        description = dash_match.group(2).strip()

        # Check if it looks like a keyboard shortcut
        shortcut_pattern = r'(?:ctrl|alt|shift|win|cmd|meta|f\d+|tab|enter|space|esc|arrows?|page\s*(?:up|down)|home|end|backspace|delete|insert)'
        if re.search(shortcut_pattern, potential_shortcut, re.IGNORECASE):
            return potential_shortcut, description

    return "", ""


def _clean_line(content: str) -> str:
    """Clean a line by removing markdown syntax, emojis, and dates."""
    # Remove emoji characters
    content = re.sub(r'[\U0001F300-\U0001F9FF]', '', content)
    content = re.sub(r'[✅🔺⏫🔽❌⬆️⬇️]', '', content)

    # Remove dates like "✅ 2025-09-29"
    content = re.sub(r'\d{4}-\d{2}-\d{2}', '', content)

    # Remove wiki links [[text]] or [[text|display]]
    content = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', content)

    # Remove markdown links [text](url)
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)

    # Clean up extra whitespace
    content = re.sub(r'\s+', ' ', content).strip()

    return content
