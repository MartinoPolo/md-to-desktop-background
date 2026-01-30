# Markdown to Desktop Background - Requirements

## Problem Statement

The user maintains a keyboard shortcuts file in Obsidian and needs a way to display unlearned shortcuts as their desktop wallpaper for daily learning reinforcement.

## Functional Requirements

### Input Processing
1. Read markdown file from configurable path (default: Obsidian vault)
2. Parse checkbox states: `[ ]` (unchecked), `[x]` (checked), `[-]` (partial)
3. Filter out checked `[x]` items (already learned)
4. Keep unchecked `[ ]` and partial `[-]` items
5. Extract shortcut from `**bold text**` markers
6. Auto-detect shortcut pattern when no bold markers present
7. Strip markdown syntax: headers, checkboxes, emojis, dates
8. Skip configurable sections by header name

### Output Generation
1. Generate PNG image at configurable resolution (default: 3200x2000)
2. Leave left 1/3 empty for desktop icons
3. Display shortcuts in two columns: shortcut key | description
4. Use different colors for different header levels
5. Support multi-column overflow when content exceeds height
6. Apply dark or light theme from configuration

### Wallpaper Integration
1. Save generated PNG to output directory
2. Set as Windows desktop wallpaper
3. Configure wallpaper style to "fill"

## Non-Functional Requirements

1. Pure Python implementation for simplicity
2. Configuration via TOML files
3. Support for common Windows fonts (Consolas, Segoe UI)
4. Command-line interface with preview mode

## Constraints

- Windows-only (uses Windows API for wallpaper)
- Python 3.10+ required
- Pillow for image generation
