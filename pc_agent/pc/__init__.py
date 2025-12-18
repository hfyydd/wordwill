"""PC utilities for desktop interaction."""

from pc_agent.pc.controller import (
    back,
    double_tap,
    get_current_app,
    home,
    launch_app,
    long_press,
    swipe,
    tap,
)
from pc_agent.pc.input import (
    clear_text,
    type_text,
    press_key,
)
from pc_agent.pc.screenshot import get_screenshot, Screenshot

__all__ = [
    # Screenshot
    "get_screenshot",
    "Screenshot",
    # Input
    "type_text",
    "clear_text",
    "press_key",
    # Device control
    "get_current_app",
    "tap",
    "swipe",
    "back",
    "home",
    "double_tap",
    "long_press",
    "launch_app",
]
