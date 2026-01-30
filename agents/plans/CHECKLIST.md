# Implementation Checklist

## Phase 1: Setup
- [x] Initialize Python project with pyproject.toml
- [x] Create directory structure
- [x] Create REQUIREMENT.md
- [x] Create CLAUDE.md
- [x] Create requirements.txt

## Phase 2: Configuration
- [x] Implement config.py - load TOML configs
- [x] Create config/config.toml with defaults
- [x] Create config/themes/dark.toml
- [x] Create config/themes/light.toml

## Phase 3: Parser
- [x] Implement parser.py
- [x] Parse headers (##, ###, ####, #####)
- [x] Parse checkbox states ([ ], [x], [-])
- [x] Extract bold shortcuts (**text**)
- [x] Auto-detect shortcuts when no bold markers
- [x] Strip markdown syntax and emojis
- [x] Filter out checked items
- [x] Skip configured sections

## Phase 4: Renderer
- [x] Implement renderer.py
- [x] Create canvas with background color
- [x] Load fonts (Consolas, Segoe UI)
- [x] Calculate layout with left 1/3 margin
- [x] Draw headers with level-specific colors
- [x] Draw two-column shortcut/description layout
- [x] Handle text alignment
- [x] Implement multi-column overflow

## Phase 5: Wallpaper
- [x] Implement wallpaper.py
- [x] Windows API integration with ctypes
- [x] Set wallpaper style (fill)

## Phase 6: Main Entry Point
- [x] Implement main.py orchestrator
- [x] CLI argument parsing
- [x] Error handling and logging

## Phase 7: Testing & Polish
- [x] Test with actual Shortcuts.md
- [x] Verify wallpaper setting works
- [x] Add preview mode (--preview flag)
