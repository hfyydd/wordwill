"""Device control utilities for PC automation."""

import os
import subprocess
import time
from typing import List, Optional, Tuple

import pyautogui
from pc_agent.config.apps import APP_CONFIGS, get_app_identifier


def get_current_app() -> str:
    """
    Get the currently focused app name.

    Returns:
        The app name if recognized, otherwise "Desktop".
    """
    try:
        # macOS specific using osascript
        script = 'tell application "System Events" to get name of first process whose frontmost is true'
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        active_app_name = result.stdout.strip()

        # Check against our config
        for name, cfg in APP_CONFIGS.items():
            if cfg.get("macos", {}).get("bundle_id") == active_app_name or name == active_app_name:
                return name
            
        return active_app_name if active_app_name else "Desktop"
    except Exception as e:
        print(f"Error getting current app: {e}")
        return "Desktop"


def tap(x: int, y: int, delay: float = 1.0) -> None:
    """
    Click at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        delay: Delay in seconds after click.
    """
    pyautogui.click(x, y)
    time.sleep(delay)


def double_tap(x: int, y: int, delay: float = 1.0) -> None:
    """
    Double click at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        delay: Delay in seconds after double click.
    """
    pyautogui.doubleClick(x, y)
    time.sleep(delay)


def long_press(x: int, y: int, duration_ms: int = 1000, delay: float = 1.0) -> None:
    """
    Long press (mouse down and hold) at the specified coordinates.

    Args:
        x: X coordinate.
        y: Y coordinate.
        duration_ms: Duration in milliseconds.
        delay: Delay in seconds after long press.
    """
    pyautogui.mouseDown(x, y)
    time.sleep(duration_ms / 1000.0)
    pyautogui.mouseUp()
    time.sleep(delay)


def swipe(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int = 500,
    delay: float = 1.0,
) -> None:
    """
    Drag from start to end coordinates.

    Args:
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Duration in milliseconds.
        delay: Delay in seconds after swipe.
    """
    pyautogui.moveTo(start_x, start_y)
    pyautogui.dragTo(end_x, end_y, duration=duration_ms / 1000.0)
    time.sleep(delay)


def back(delay: float = 1.0) -> None:
    """
    Perform a 'back' action. On macOS, this is often Cmd+[ .
    """
    with pyautogui.hold('command'):
        pyautogui.press('[')
    time.sleep(delay)


def home(delay: float = 1.0) -> None:
    """
    Perform a 'home' action. On macOS, this could be Cmd+Mission Control or similar.
    Here we'll use a common 'Show Desktop' shortcut if possible, or just a placeholder.
    """
    # Command + F3 is 'Show Desktop' on many Macs
    with pyautogui.hold('command'):
        pyautogui.press('f3')
    time.sleep(delay)


def launch_app(app_name: str, delay: float = 2.0) -> bool:
    """
    Launch an app by name.

    Args:
        app_name: The app name (must be in APP_CONFIGS).
        delay: Delay in seconds after launching.

    Returns:
        True if app was launched, False if app not found.
    """
    bundle_id = get_app_identifier(app_name, platform="macos")
    if not bundle_id:
        return False

    try:
        # macOS: open -b <bundle_id>
        subprocess.run(['open', '-b', bundle_id], check=True)
        time.sleep(delay)
        return True
    except Exception as e:
        print(f"Error launching app {app_name}: {e}")
        return False
