"""Main entry point for the markdown to desktop background tool."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .config import load_config
from .parser import parse_markdown
from .renderer import render_to_image
from .wallpaper import set_wallpaper, set_wallpaper_style


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert markdown shortcuts to desktop wallpaper"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to config directory (default: ./config)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Generate image but don't set as wallpaper",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Override output file path",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Override input markdown file path",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config_dir = args.config or Path(__file__).parent.parent / "config"
        print(f"Loading config from: {config_dir}")
        config = load_config(config_dir)

        # Determine input file
        input_file = args.input or Path(config.source.markdown_file)
        print(f"Reading markdown from: {input_file}")

        if not input_file.exists():
            print(f"Error: Input file not found: {input_file}")
            sys.exit(1)

        # Parse markdown
        print("Parsing markdown...")
        content = parse_markdown(
            input_file,
            skip_sections=config.filter.skip_sections,
            include_partial=config.filter.include_partial,
        )

        # Count items
        from .parser import HeaderItem, ShortcutItem
        headers = sum(1 for item in content.items if isinstance(item, HeaderItem))
        shortcuts = sum(1 for item in content.items if isinstance(item, ShortcutItem))
        print(f"Found {headers} sections and {shortcuts} shortcuts")

        # Render image
        print(f"Rendering image ({config.display.width}x{config.display.height})...")
        image = render_to_image(content, config)

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            output_dir = Path(config.output.directory)
            output_dir.mkdir(parents=True, exist_ok=True)

            filename = config.output.filename.format(
                date=datetime.now().strftime("%Y-%m-%d")
            )
            output_path = output_dir / filename

        # Save image
        print(f"Saving to: {output_path}")
        image.save(output_path, "PNG")

        # Set wallpaper (unless preview mode)
        if args.preview:
            print("Preview mode - wallpaper not changed")
        else:
            print("Setting wallpaper style to 'fill'...")
            set_wallpaper_style("fill")

            print("Setting wallpaper...")
            if set_wallpaper(output_path):
                print("Wallpaper set successfully!")
            else:
                print("Warning: Failed to set wallpaper")

        print("Done!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
