# Markdown to Desktop Background

A Python tool that converts a Markdown file containing keyboard shortcuts into a styled desktop wallpaper image, then sets it as the Windows background.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run (generates wallpaper and sets it)
python -m src.main

# Preview only (don't set wallpaper)
python -m src.main --preview
```

## Project Structure

- `src/` - Python source code
  - `main.py` - Entry point
  - `parser.py` - Markdown parsing and filtering
  - `renderer.py` - Image generation with Pillow
  - `wallpaper.py` - Windows wallpaper API
  - `config.py` - Configuration loading
- `config/` - Configuration files
  - `config.toml` - Main configuration
  - `themes/` - Color themes (dark.toml, light.toml)
- `output/` - Generated wallpaper images

## Configuration

Edit `config/config.toml` to customize:
- Source markdown file path
- Output resolution and filename
- Theme (dark/light)
- Fonts and sizes
- Sections to skip

## How It Works

1. Reads a markdown file with keyboard shortcuts
2. Filters out learned shortcuts (marked with `[x]`)
3. Keeps unlearned (`[ ]`) and partial (`[-]`) items
4. Extracts shortcut from **bold** text or auto-detects patterns
5. Renders to an image using a 3-column grid with selectable active columns
6. Sets as Windows wallpaper using the system API
