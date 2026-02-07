"""Image rendering with Pillow."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import List, Optional, Tuple

from .config import Config, ThemeColors
from .parser import ParsedContent, HeaderItem, ShortcutItem


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def load_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a font by name, with fallback to default."""
    # Common Windows font paths
    font_paths = [
        f"C:/Windows/Fonts/{font_name}.ttf",
        f"C:/Windows/Fonts/{font_name.lower()}.ttf",
        f"C:/Windows/Fonts/{font_name.replace(' ', '')}.ttf",
    ]

    # Add specific mappings for common fonts
    font_mappings = {
        "Consolas": "consola.ttf",
        "Segoe UI": "segoeui.ttf",
        "Segoe UI Bold": "segoeuib.ttf",
        "Arial": "arial.ttf",
        "Courier New": "cour.ttf",
        "Cascadia Code": "CascadiaCode.ttf",
        "Cascadia Mono": "CascadiaMono.ttf",
        "Fira Code": "FiraCode-Regular.ttf",
        "JetBrains Mono": "JetBrainsMono-Regular.ttf",
        "Source Code Pro": "SourceCodePro-Regular.ttf",
        "Roboto Mono": "RobotoMono-Regular.ttf",
        "Ubuntu Mono": "UbuntuMono-R.ttf",
        "Hack": "Hack-Regular.ttf",
        "Inconsolata": "Inconsolata-Regular.ttf",
        "Lucida Console": "lucon.ttf",
        "Calibri": "calibri.ttf",
        "Georgia": "georgia.ttf",
    }

    if font_name in font_mappings:
        font_paths.insert(0, f"C:/Windows/Fonts/{font_mappings[font_name]}")

    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    # Fallback to default
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


class Renderer:
    """Renders parsed content to an image."""

    def __init__(self, config: Config, font_size_override: Optional[int] = None):
        self.config = config
        self.width = config.display.width
        self.height = config.display.height
        self.theme = config.theme

        # Use override or config font size
        self.shortcut_size = font_size_override or config.fonts.shortcut_size
        self.description_size = int(self.shortcut_size * 0.9)  # Description slightly smaller
        self.header_size = self.shortcut_size + 4

        # Load fonts with current sizes
        self._load_fonts()

        # Fixed 3-column grid
        self.edge_padding = 50
        self.top_margin = 50
        self.bottom_margin = 50
        self.column_width = (self.width - 2 * self.edge_padding) // 3
        self.column_positions = {
            "left": self.edge_padding,
            "middle": self.edge_padding + self.column_width,
            "right": self.edge_padding + 2 * self.column_width,
        }
        self.active_columns = config.layout.active_columns
        self.shortcut_column_width = int(self.column_width * 0.35)

    def _load_fonts(self):
        """Load fonts with current sizes."""
        self.header_font = load_font(self.config.fonts.header_font, self.header_size)
        self.shortcut_font = load_font(self.config.fonts.shortcut_font, self.shortcut_size)
        self.description_font = load_font(self.config.fonts.description_font, self.description_size)

    def render(self, content: ParsedContent) -> Image.Image:
        """Render parsed content to an image."""
        bg_color = hex_to_rgb(self.theme.background)
        image = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)

        line_height = int(self.shortcut_size * self.config.layout.line_height)
        header_height = int(self.header_size * self.config.layout.line_height)
        available_height = self.height - self.top_margin - self.bottom_margin

        # Always split across all active columns
        active_positions = [self.column_positions[c] for c in self.active_columns]
        num_columns = len(active_positions)

        if num_columns > 1:
            columns = self._split_into_columns(content, num_columns, available_height, line_height, header_height)
        else:
            columns = [content.items]

        for col_idx, column_items in enumerate(columns):
            self._render_column(draw, column_items, active_positions[col_idx], line_height, header_height)

        return image

    def _calculate_content_height(
        self,
        content: ParsedContent,
        line_height: int,
        header_height: int,
    ) -> int:
        """Calculate total height needed for content."""
        total = 0
        for item in content.items:
            if isinstance(item, HeaderItem):
                total += header_height + self.config.layout.section_gap
            else:
                total += line_height
        return total

    def _split_into_columns(
        self,
        content: ParsedContent,
        num_columns: int,
        available_height: int,
        line_height: int,
        header_height: int,
    ) -> List[List]:
        """Split content into roughly equal columns."""
        total_height = self._calculate_content_height(content, line_height, header_height)
        target_height = total_height // num_columns

        columns = []
        current_column = []
        current_height = 0

        for item in content.items:
            if isinstance(item, HeaderItem):
                item_height = header_height + self.config.layout.section_gap
            else:
                item_height = line_height

            # Check if adding this item would exceed target (unless column is empty)
            if current_height + item_height > target_height and current_column and len(columns) < num_columns - 1:
                # Try not to split right after a header
                if isinstance(item, ShortcutItem) and current_column and isinstance(current_column[-1], HeaderItem):
                    # Move header to next column
                    header = current_column.pop()
                    columns.append(current_column)
                    current_column = [header]
                    current_height = header_height + self.config.layout.section_gap
                else:
                    columns.append(current_column)
                    current_column = []
                    current_height = 0

            current_column.append(item)
            current_height += item_height

        if current_column:
            columns.append(current_column)

        return columns

    def _render_column(
        self,
        draw: ImageDraw.Draw,
        items: list,
        x_start: int,
        line_height: int,
        header_height: int,
    ):
        """Render a single column of items."""
        y = self.top_margin
        desc_x = x_start + self.shortcut_column_width + self.config.layout.column_gap

        for item in items:
            if isinstance(item, HeaderItem):
                if y > self.top_margin:
                    y += self.config.layout.section_gap // 2

                color = self._get_header_color(item.level)
                draw.text(
                    (x_start, y),
                    item.text,
                    font=self.header_font,
                    fill=color,
                )
                y += header_height
                y += self.config.layout.section_gap // 2

            elif isinstance(item, ShortcutItem):
                shortcut_color = hex_to_rgb(self.theme.shortcut)
                draw.text(
                    (x_start, y),
                    item.shortcut,
                    font=self.shortcut_font,
                    fill=shortcut_color,
                )

                if item.description:
                    desc_color = hex_to_rgb(self.theme.description)
                    desc = self._truncate_text(
                        item.description,
                        self.column_width - self.shortcut_column_width - self.config.layout.column_gap,
                    )
                    draw.text(
                        (desc_x, y),
                        desc,
                        font=self.description_font,
                        fill=desc_color,
                    )

                y += line_height

    def _get_header_color(self, level: int) -> Tuple[int, int, int]:
        """Get color for header level."""
        color_map = {
            2: self.theme.header_h2,
            3: self.theme.header_h3,
            4: self.theme.header_h4,
            5: self.theme.header_h5,
        }
        hex_color = color_map.get(level, self.theme.header_h2)
        return hex_to_rgb(hex_color)

    def _truncate_text(self, text: str, max_width: int) -> str:
        """Truncate text to fit within max_width pixels."""
        if not text:
            return text

        # Create a temporary image for text measurement
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)

        bbox = temp_draw.textbbox((0, 0), text, font=self.description_font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            return text

        # Binary search for the right length
        ellipsis = "..."
        low, high = 0, len(text)

        while low < high:
            mid = (low + high + 1) // 2
            truncated = text[:mid] + ellipsis
            bbox = temp_draw.textbbox((0, 0), truncated, font=self.description_font)
            if bbox[2] - bbox[0] <= max_width:
                low = mid
            else:
                high = mid - 1

        return text[:low] + ellipsis if low < len(text) else text


def find_optimal_font_size(
    content: ParsedContent,
    config: Config,
    min_size: int = 14,
    max_size: int = 40,
) -> int:
    """Find the optimal font size to fill available space.

    Uses binary search to find the largest font size where content
    still fits within the available height (with configured columns).
    """
    available_height = config.display.height - 100  # top + bottom margin

    def content_fits(font_size: int) -> bool:
        """Check if content fits with given font size."""
        line_height = int(font_size * config.layout.line_height)
        header_height = int((font_size + 4) * config.layout.line_height)

        total_height = 0
        for item in content.items:
            if isinstance(item, HeaderItem):
                total_height += header_height + config.layout.section_gap
            else:
                total_height += line_height

        # Account for multiple columns
        num_columns = len(config.layout.active_columns)
        height_per_column = total_height / num_columns

        return height_per_column <= available_height

    # Binary search for optimal size
    low, high = min_size, max_size
    optimal = min_size

    while low <= high:
        mid = (low + high) // 2
        if content_fits(mid):
            optimal = mid
            low = mid + 1
        else:
            high = mid - 1

    return optimal


def render_to_image(
    content: ParsedContent,
    config: Config,
    auto_scale: bool = True,
) -> Image.Image:
    """Render content to an image.

    Args:
        content: Parsed markdown content
        config: Configuration object
        auto_scale: If True, automatically scale font to fill available space
    """
    if auto_scale:
        optimal_size = find_optimal_font_size(content, config)
        print(f"Auto-scaled font size: {optimal_size}px")
        renderer = Renderer(config, font_size_override=optimal_size)
    else:
        renderer = Renderer(config)

    return renderer.render(content)
