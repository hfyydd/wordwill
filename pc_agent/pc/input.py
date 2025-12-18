"""Input utilities for PC interaction."""

import pyautogui
import time
import pyperclip


def type_text(text: str, delay: float = 0.1) -> None:
    """
    Type the specified text. Handles Chinese characters via clipboard.

    Args:
        text: Text to type.
        delay: Delay between keystrokes (only used for ASCII text).
    """
    try:
        # Check if text is pure ASCII
        text.encode('ascii')
        pyautogui.write(text, interval=delay)
    except UnicodeEncodeError:
        # Contains non-ASCII (e.g. Chinese), use clipboard
        pyperclip.copy(text)
        time.sleep(0.1)  # Brief wait for clipboard to update
        
        # Determine modifier based on OS (user is on Mac)
        # Using command for Mac, control for others
        # Based on existing clear_text, we know user is on Mac
        with pyautogui.hold('command'):
            pyautogui.press('v')


def clear_text() -> None:
    """
    Clear text in the current focused element.
    On PC, this usually involves selecting all and deleting.
    """
    # Cmd+A and Backspace for macOS, Ctrl+A and Backspace for others
    # Since the user is on Mac, we use command
    with pyautogui.hold('command'):
        pyautogui.press('a')
    pyautogui.press('backspace')


def press_key(key: str) -> None:
    """
    Press a specific key.
    
    Args:
        key: Key name (e.g., 'enter', 'esc', 'tab').
    """
    pyautogui.press(key)
