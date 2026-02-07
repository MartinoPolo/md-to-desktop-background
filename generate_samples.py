"""Generate sample wallpapers with per-property variations."""

import copy
from pathlib import Path

from src.config import load_config, ThemeColors, FontsConfig, LayoutConfig
from src.parser import parse_markdown
from src.renderer import render_to_image, find_optimal_font_size, Renderer

# Shared defaults: black BG, Consolas/Segoe UI, Dracula FG, red/cyan/green/brown headers
DEFAULT_THEME = ThemeColors(
    background="#000000",
    header_h2="#e94560",
    header_h3="#0f94b3",
    header_h4="#44a363",
    header_h5="#9c7b4a",
    shortcut="#f8f8f2",
    description="#6272a4",
)
DEFAULT_FONTS = {"shortcut_font": "Consolas", "description_font": "Segoe UI"}

# --- Group 1: Fonts ---
FONTS = [
    ("01_consolas_segoeui", "Consolas / Segoe UI (default)", {"shortcut_font": "Consolas", "description_font": "Segoe UI"}),
    ("02_couriernew_arial", "Courier New / Arial", {"shortcut_font": "Courier New", "description_font": "Arial"}),
    ("03_arial_arial", "Arial / Arial", {"shortcut_font": "Arial", "description_font": "Arial"}),
    ("04_lucidaconsole_segoeui", "Lucida Console / Segoe UI", {"shortcut_font": "Lucida Console", "description_font": "Segoe UI"}),
    ("05_segoeui_segoeui", "Segoe UI / Segoe UI", {"shortcut_font": "Segoe UI", "description_font": "Segoe UI"}),
    ("06_calibri_calibri", "Calibri / Calibri", {"shortcut_font": "Calibri", "description_font": "Calibri"}),
    ("07_consolas_calibri", "Consolas / Calibri", {"shortcut_font": "Consolas", "description_font": "Calibri"}),
    ("08_georgia_georgia", "Georgia / Georgia", {"shortcut_font": "Georgia", "description_font": "Georgia"}),
    ("09_couriernew_segoeui", "Courier New / Segoe UI", {"shortcut_font": "Courier New", "description_font": "Segoe UI"}),
    ("10_lucidaconsole_calibri", "Lucida Console / Calibri", {"shortcut_font": "Lucida Console", "description_font": "Calibri"}),
]

# --- Group 2: Background Colors ---
BACKGROUNDS = [
    ("01_pure_black", "Pure black (default)", "#000000"),
    ("02_near_black", "Near-black", "#0a0a0a"),
    ("03_dark_blue_gray", "Dark blue-gray", "#0d0d1a"),
    ("04_navy", "Navy", "#0a1420"),
    ("05_vscode_dark", "VS Code dark", "#1e1e1e"),
    ("06_slate", "Dark slate", "#1a1f21"),
    ("07_midnight", "Midnight", "#08081a"),
    ("08_dark_purple", "Dark purple", "#0e0618"),
    ("09_warm_brown", "Dark brown", "#100c08"),
    ("10_ocean_navy", "Ocean navy", "#06101f"),
    ("11_dark_teal", "Dark teal", "#060f0f"),
    ("12_dark_olive", "Dark olive", "#0a0e06"),
    ("13_dark_wine", "Dark wine", "#120608"),
    ("14_charcoal_blue", "Charcoal blue", "#0c1014"),
]

# --- Group 3: Foreground Colors ---
FOREGROUNDS = [
    ("01_dracula", "Dracula (default)", "#f8f8f2", "#6272a4"),
    ("02_white_powder_blue", "White / powder blue", "#ffffff", "#8899bb"),
    ("03_bright_white_steel", "Bright white / steel blue", "#ffffff", "#7088a8"),
    ("04_white_slate_blue", "White / slate blue", "#f0f0f0", "#5c6d8e"),
    ("05_white_periwinkle", "White / periwinkle", "#f5f5f5", "#7a82b0"),
    ("06_white_dusk_blue", "White / dusk blue", "#fafafa", "#4e6180"),
    ("07_white_cornflower", "White / cornflower", "#f8f8f8", "#6b85b5"),
    ("08_white_cadet_blue", "White / cadet blue", "#eeeeee", "#5f8fa0"),
    ("09_white_muted_indigo", "White / muted indigo", "#f2f2f2", "#6868a0"),
    ("10_white_twilight", "White / twilight blue", "#f4f4f0", "#556b8a"),
]

# --- Group 4: Header Color Schemes ---
HEADERS = [
    ("01_red_cyan_green_brown", "Red/Cyan/Green/Brown (default)", "#e94560", "#0f94b3", "#44a363", "#9c7b4a"),
    ("02_gold_cyan_pink_lime", "Gold/Cyan/Pink/Lime", "#ffcc00", "#00ccff", "#ff6699", "#99ff66"),
    ("03_coral_mint_blue_sage", "Coral/Mint/Blue/Sage", "#ff6b6b", "#55efc4", "#74b9ff", "#a3cb38"),
    ("04_dracula", "Dracula", "#ff79c6", "#8be9fd", "#50fa7b", "#ffb86c"),
    ("05_white_blue_mint_yellow", "White/Blue/Mint/Yellow", "#dfe6e9", "#74b9ff", "#55efc4", "#ffeaa7"),
    ("06_one_dark", "One Dark", "#98c379", "#c678dd", "#e5c07b", "#61afef"),
    ("07_matrix", "Mono green", "#00ff41", "#00cc33", "#009926", "#006619"),
    ("08_purple_gradient", "Purple gradient", "#e0aaff", "#c77dff", "#9d4edd", "#7b2cbf"),
    ("09_warm", "Warm reds/oranges", "#ff4444", "#ff9f43", "#ee5a24", "#f368e0"),
    ("10_cool_blues", "Cool blues/teals", "#64ffda", "#45a29e", "#74b9ff", "#0f94b3"),
]

# --- Group 5: Layout Variations ---
# Fixed 3-column grid. Only which columns are active varies.
LAYOUTS = [
    ("01_left", "1 column, left", {"active_columns": ["left"]}),
    ("02_middle", "1 column, middle", {"active_columns": ["middle"]}),
    ("03_right", "1 column, right", {"active_columns": ["right"]}),
    ("04_left_middle", "2 columns, left + middle", {"active_columns": ["left", "middle"]}),
    ("05_middle_right", "2 columns, middle + right (default)", {"active_columns": ["middle", "right"]}),
    ("06_all", "3 columns", {"active_columns": ["left", "middle", "right"]}),
]


def make_config(base_config, theme_overrides=None, font_overrides=None, layout_overrides=None):
    """Create a modified config from base with selective overrides."""
    config = copy.deepcopy(base_config)

    # Apply default theme, then overrides
    config.theme = copy.deepcopy(DEFAULT_THEME)
    if theme_overrides:
        for key, value in theme_overrides.items():
            setattr(config.theme, key, value)

    # Apply default fonts, then overrides
    for key, value in DEFAULT_FONTS.items():
        setattr(config.fonts, key, value)
    if font_overrides:
        for key, value in font_overrides.items():
            setattr(config.fonts, key, value)

    # Apply layout overrides
    if layout_overrides:
        for key, value in layout_overrides.items():
            setattr(config.layout, key, value)

    return config


def generate_group(base_config, content, group_name, samples_dir, items, config_builder):
    """Generate a group of samples."""
    group_dir = samples_dir / group_name
    group_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== {group_name.upper()} ({len(items)} samples) ===")

    for item in items:
        name, description = item[0], item[1]
        config = config_builder(base_config, item)

        print(f"  {name} - {description}")
        image = render_to_image(content, config, auto_scale=True)

        output_path = group_dir / f"{name}.png"
        image.save(output_path, "PNG")


def main():
    base_config = load_config()

    content = parse_markdown(
        base_config.source.markdown_file,
        skip_sections=base_config.filter.skip_sections,
        include_partial=base_config.filter.include_partial,
    )

    samples_dir = Path("output/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fonts
    generate_group(base_config, content, "fonts", samples_dir, FONTS,
        lambda cfg, item: make_config(cfg, font_overrides=item[2]))

    # 2. Backgrounds
    generate_group(base_config, content, "backgrounds", samples_dir, BACKGROUNDS,
        lambda cfg, item: make_config(cfg, theme_overrides={"background": item[2]}))

    # 3. Foregrounds
    generate_group(base_config, content, "foregrounds", samples_dir, FOREGROUNDS,
        lambda cfg, item: make_config(cfg, theme_overrides={"shortcut": item[2], "description": item[3]}))

    # 4. Headers
    generate_group(base_config, content, "headers", samples_dir, HEADERS,
        lambda cfg, item: make_config(cfg, theme_overrides={
            "header_h2": item[2], "header_h3": item[3],
            "header_h4": item[4], "header_h5": item[5],
        }))

    # 5. Layouts — fixed font size across all variations (computed from 2-col reference)
    reference_config = make_config(base_config, layout_overrides={"active_columns": ["middle", "right"]})
    reference_font_size = find_optimal_font_size(content, reference_config)
    print(f"\n  Layout reference font size: {reference_font_size}px")

    def make_layout_config(cfg, item):
        config = make_config(cfg, layout_overrides=item[2])
        return config

    layout_dir = samples_dir / "layouts"
    layout_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=== LAYOUTS ({len(LAYOUTS)} samples) ===")
    for item in LAYOUTS:
        name, description = item[0], item[1]
        config = make_layout_config(base_config, item)
        print(f"  {name} - {description}")
        renderer = Renderer(config, font_size_override=reference_font_size)
        image = renderer.render(content)
        output_path = layout_dir / f"{name}.png"
        image.save(output_path, "PNG")

    total = len(FONTS) + len(BACKGROUNDS) + len(FOREGROUNDS) + len(HEADERS) + len(LAYOUTS)
    print(f"\nDone! Generated {total} samples in {samples_dir}")


if __name__ == "__main__":
    main()
