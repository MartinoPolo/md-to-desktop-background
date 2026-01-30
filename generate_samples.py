"""Generate sample wallpapers with different configurations."""

import copy
from pathlib import Path
from dataclasses import replace

from src.config import load_config, ThemeColors, FontsConfig
from src.parser import parse_markdown
from src.renderer import render_to_image

# Define sample configurations
SAMPLES = [
    {
        "name": "01_dark_consolas",
        "description": "Original dark theme with Consolas",
        "theme": ThemeColors(
            background="#1a1a2e",
            header_h2="#e94560",
            header_h3="#0f94b3",
            header_h4="#44a363",
            header_h5="#9c7b4a",
            shortcut="#ffffff",
            description="#b0b0b0",
        ),
        "fonts": {"shortcut_font": "Consolas", "description_font": "Segoe UI"},
    },
    {
        "name": "02_darker_cascadia",
        "description": "Darker background with Cascadia Code",
        "theme": ThemeColors(
            background="#0a0a14",
            header_h2="#ff6b6b",
            header_h3="#4ecdc4",
            header_h4="#45b7d1",
            header_h5="#96ceb4",
            shortcut="#e8e8e8",
            description="#888888",
        ),
        "fonts": {"shortcut_font": "Cascadia Code", "description_font": "Segoe UI"},
    },
    {
        "name": "03_pure_black_courier",
        "description": "Pure black background with Courier New",
        "theme": ThemeColors(
            background="#000000",
            header_h2="#ff4444",
            header_h3="#44ff44",
            header_h4="#4444ff",
            header_h5="#ffff44",
            shortcut="#ffffff",
            description="#999999",
        ),
        "fonts": {"shortcut_font": "Courier New", "description_font": "Arial"},
    },
    {
        "name": "04_navy_segoe",
        "description": "Navy blue background with Segoe UI",
        "theme": ThemeColors(
            background="#0d1b2a",
            header_h2="#e0aaff",
            header_h3="#c77dff",
            header_h4="#9d4edd",
            header_h5="#7b2cbf",
            shortcut="#e8f4f8",
            description="#778da9",
        ),
        "fonts": {"shortcut_font": "Segoe UI", "description_font": "Segoe UI"},
    },
    {
        "name": "05_charcoal_green_accent",
        "description": "Charcoal with green accents",
        "theme": ThemeColors(
            background="#1e1e1e",
            header_h2="#98c379",
            header_h3="#61afef",
            header_h4="#c678dd",
            header_h5="#e5c07b",
            shortcut="#abb2bf",
            description="#5c6370",
        ),
        "fonts": {"shortcut_font": "Consolas", "description_font": "Segoe UI"},
    },
    {
        "name": "06_midnight_blue_cascadia",
        "description": "Midnight blue with warm colors",
        "theme": ThemeColors(
            background="#0f0f23",
            header_h2="#ffcc00",
            header_h3="#00ccff",
            header_h4="#ff6699",
            header_h5="#99ff66",
            shortcut="#cccccc",
            description="#666680",
        ),
        "fonts": {"shortcut_font": "Cascadia Mono", "description_font": "Segoe UI"},
    },
    {
        "name": "07_dark_purple_high_contrast",
        "description": "Dark purple with high contrast",
        "theme": ThemeColors(
            background="#1a0a2e",
            header_h2="#ff79c6",
            header_h3="#8be9fd",
            header_h4="#50fa7b",
            header_h5="#ffb86c",
            shortcut="#f8f8f2",
            description="#6272a4",
        ),
        "fonts": {"shortcut_font": "Consolas", "description_font": "Segoe UI"},
    },
    {
        "name": "08_slate_minimal",
        "description": "Slate gray minimal design",
        "theme": ThemeColors(
            background="#2d3436",
            header_h2="#dfe6e9",
            header_h3="#74b9ff",
            header_h4="#55efc4",
            header_h5="#ffeaa7",
            shortcut="#b2bec3",
            description="#636e72",
        ),
        "fonts": {"shortcut_font": "Arial", "description_font": "Arial"},
    },
    {
        "name": "09_deep_space_courier",
        "description": "Deep space theme",
        "theme": ThemeColors(
            background="#0b0c10",
            header_h2="#66fcf1",
            header_h3="#45a29e",
            header_h4="#c5c6c7",
            header_h5="#1f2833",
            shortcut="#c5c6c7",
            description="#66fcf1",
        ),
        "fonts": {"shortcut_font": "Courier New", "description_font": "Segoe UI"},
    },
    {
        "name": "10_warm_dark",
        "description": "Warm dark theme with orange accents",
        "theme": ThemeColors(
            background="#1c1410",
            header_h2="#ff9f43",
            header_h3="#ee5a24",
            header_h4="#f368e0",
            header_h5="#00d2d3",
            shortcut="#ffeaa7",
            description="#a29382",
        ),
        "fonts": {"shortcut_font": "Consolas", "description_font": "Segoe UI"},
    },
    {
        "name": "11_matrix_green",
        "description": "Matrix-inspired green theme",
        "theme": ThemeColors(
            background="#0d0208",
            header_h2="#00ff41",
            header_h3="#008f11",
            header_h4="#00ff41",
            header_h5="#003b00",
            shortcut="#00ff41",
            description="#008f11",
        ),
        "fonts": {"shortcut_font": "Courier New", "description_font": "Courier New"},
    },
    {
        "name": "12_ocean_blue",
        "description": "Ocean blue gradient feel",
        "theme": ThemeColors(
            background="#0a192f",
            header_h2="#64ffda",
            header_h3="#ccd6f6",
            header_h4="#8892b0",
            header_h5="#233554",
            shortcut="#ccd6f6",
            description="#8892b0",
        ),
        "fonts": {"shortcut_font": "Cascadia Code", "description_font": "Segoe UI"},
    },
]


def main():
    # Load base config
    config = load_config()

    # Parse markdown once
    content = parse_markdown(
        config.source.markdown_file,
        skip_sections=config.filter.skip_sections,
        include_partial=config.filter.include_partial,
    )

    # Create output directory for samples
    samples_dir = Path("output/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(SAMPLES)} sample wallpapers...\n")

    for sample in SAMPLES:
        print(f"Generating: {sample['name']} - {sample['description']}")

        # Create modified config
        modified_config = copy.deepcopy(config)
        modified_config.theme = sample["theme"]

        # Update fonts if specified
        if "fonts" in sample:
            for key, value in sample["fonts"].items():
                setattr(modified_config.fonts, key, value)

        # Render image with auto-scaling
        image = render_to_image(content, modified_config, auto_scale=True)

        # Save
        output_path = samples_dir / f"{sample['name']}.png"
        image.save(output_path, "PNG")
        print(f"  Saved to: {output_path}\n")

    print(f"Done! Generated {len(SAMPLES)} samples in {samples_dir}")


if __name__ == "__main__":
    main()
