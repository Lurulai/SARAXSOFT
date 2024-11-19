"""Image utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from PIL import Image, ImageTk

if TYPE_CHECKING:
    from pathlib import Path


def load_image(path: Path, size: tuple[int, int]) -> ImageTk.PhotoImage | None:
    """
    Load image from the given path.

    Parameters
    ----------
    path : Path
        The path of the image.
    size : tuple[int, int]
        Size to resize the image to.

    Return
    ------
    ImageTk.PhotoImage | None
        The photo image or None if path not found.
    """
    try:
        img = Image.open(path)
        img = img.resize(size)
        return ImageTk.PhotoImage(img)
    except Exception:  # noqa: BLE001
        logger.error(f"Could not find the provided image. Ensure the provided path `{path}` is correct.")
        return None
