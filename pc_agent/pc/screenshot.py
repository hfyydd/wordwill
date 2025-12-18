"""Screenshot utilities for capturing PC screen."""

import base64
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import pyautogui
from PIL import Image


@dataclass
class Screenshot:
    """Represents a captured screenshot."""

    base64_data: str
    width: int
    height: int
    logical_width: int = 0
    logical_height: int = 0
    is_sensitive: bool = False


def get_screenshot(timeout: int = 10) -> Screenshot:
    """
    Capture a screenshot from the PC screen.

    Returns:
        Screenshot object containing base64 data and dimensions.
    """
    try:
        # Capture screenshot using pyautogui
        img = pyautogui.screenshot()
        width, height = img.size
        
        # Get logical screen size for coordinate conversion
        try:
            logical_width, logical_height = pyautogui.size()
        except:
            logical_width, logical_height = width, height

        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return Screenshot(
            base64_data=base64_data, 
            width=width, 
            height=height, 
            logical_width=logical_width,
            logical_height=logical_height,
            is_sensitive=False
        )

    except Exception as e:
        print(f"Screenshot error: {e}")
        return _create_fallback_screenshot(is_sensitive=False)


def _create_fallback_screenshot(is_sensitive: bool) -> Screenshot:
    """Create a black fallback image when screenshot fails."""
    # Use screen size if available, otherwise default
    try:
        default_width, default_height = pyautogui.size()
    except:
        default_width, default_height = 1920, 1080

    black_img = Image.new("RGB", (default_width, default_height), color="black")
    buffered = BytesIO()
    black_img.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return Screenshot(
        base64_data=base64_data,
        width=default_width,
        height=default_height,
        is_sensitive=is_sensitive,
    )
