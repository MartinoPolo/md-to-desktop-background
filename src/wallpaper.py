"""Windows wallpaper API integration."""
from __future__ import annotations

import ctypes
from pathlib import Path
from typing import Union


# Windows API constants
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


def set_wallpaper(image_path: Union[str, Path]) -> bool:
    """Set the Windows desktop wallpaper.

    Args:
        image_path: Path to the image file (must be absolute)

    Returns:
        True if successful, False otherwise
    """
    image_path = Path(image_path).resolve()

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Convert to string with proper Windows path format
    path_str = str(image_path)

    # Call Windows API
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        path_str,
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )

    return bool(result)


def set_wallpaper_style(style: str = "fill") -> bool:
    """Set the wallpaper display style.

    Args:
        style: One of "fill", "fit", "stretch", "tile", "center", "span"

    Returns:
        True if successful
    """
    import winreg

    # Style values for Windows registry
    styles = {
        "fill": ("10", "0"),      # WallpaperStyle=10, TileWallpaper=0
        "fit": ("6", "0"),        # WallpaperStyle=6, TileWallpaper=0
        "stretch": ("2", "0"),    # WallpaperStyle=2, TileWallpaper=0
        "tile": ("0", "1"),       # WallpaperStyle=0, TileWallpaper=1
        "center": ("0", "0"),     # WallpaperStyle=0, TileWallpaper=0
        "span": ("22", "0"),      # WallpaperStyle=22, TileWallpaper=0
    }

    if style not in styles:
        raise ValueError(f"Unknown style: {style}. Must be one of: {', '.join(styles.keys())}")

    wallpaper_style, tile = styles[style]

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Control Panel\Desktop",
            0,
            winreg.KEY_SET_VALUE
        )

        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, wallpaper_style)
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, tile)
        winreg.CloseKey(key)

        return True
    except Exception as e:
        print(f"Failed to set wallpaper style: {e}")
        return False
