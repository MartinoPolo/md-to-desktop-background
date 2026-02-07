"""Configuration loading from TOML files."""
from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib


@dataclass
class SourceItem:
    path: str = ""
    format: str = "markdown"
    title: str = ""


@dataclass
class SourceConfig:
    items: List[SourceItem] = field(default_factory=list)


@dataclass
class OutputConfig:
    directory: str = "./output"
    filename: str = "shortcuts-{date}.png"


@dataclass
class DisplayConfig:
    resolution: str = "3200x2000"
    theme: str = "dark"

    @property
    def width(self) -> int:
        return int(self.resolution.split("x")[0])

    @property
    def height(self) -> int:
        return int(self.resolution.split("x")[1])


@dataclass
class LayoutConfig:
    column_gap: int = 40
    line_height: float = 1.5
    section_gap: int = 30
    active_columns: List[str] = field(default_factory=lambda: ["middle", "right"])


@dataclass
class FontsConfig:
    shortcut_font: str = "Consolas"
    shortcut_size: int = 22
    description_font: str = "Segoe UI"
    description_size: int = 20
    header_font: str = "Segoe UI"


@dataclass
class FilterConfig:
    skip_sections: List[str] = field(default_factory=list)
    include_partial: bool = True


@dataclass
class ThemeColors:
    background: str = "#000000"
    header_h2: str = "#e94560"
    header_h3: str = "#0f94b3"
    header_h4: str = "#44a363"
    header_h5: str = "#9c7b4a"
    shortcut: str = "#f8f8f2"
    description: str = "#6272a4"


@dataclass
class Config:
    source: SourceConfig
    output: OutputConfig
    display: DisplayConfig
    layout: LayoutConfig
    fonts: FontsConfig
    filter: FilterConfig
    theme: ThemeColors


def load_config(config_dir: Optional[Path] = None) -> Config:
    """Load configuration from TOML files."""
    if config_dir is None:
        config_dir = Path(__file__).parent.parent / "config"

    config_path = config_dir / "config.toml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    # Load sources list
    sources_data = data.get("sources", [])
    source_items = [SourceItem(**s) for s in sources_data]
    source = SourceConfig(items=source_items)

    output = OutputConfig(**data.get("output", {}))
    display = DisplayConfig(**data.get("display", {}))
    layout = LayoutConfig(**data.get("layout", {}))
    fonts = FontsConfig(**data.get("fonts", {}))
    filter_cfg = FilterConfig(**data.get("filter", {}))

    # Load theme
    theme_name = display.theme
    theme_path = config_dir / "themes" / f"{theme_name}.toml"

    if theme_path.exists():
        with open(theme_path, "rb") as f:
            theme_data = tomllib.load(f)
        theme = ThemeColors(**theme_data.get("colors", {}))
    else:
        theme = ThemeColors()

    return Config(
        source=source,
        output=output,
        display=display,
        layout=layout,
        fonts=fonts,
        filter=filter_cfg,
        theme=theme,
    )
