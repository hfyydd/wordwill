"""Action handler for processing AI model outputs."""

import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple, Dict, Union, List

from pc_agent.pc import (
    back,
    clear_text,
    double_tap,
    home,
    launch_app,
    long_press,
    swipe,
    tap,
    type_text,
)


@dataclass
class ActionResult:
    """Result of an action execution."""

    success: bool
    should_finish: bool
    message: Optional[str] = None
    requires_confirmation: bool = False


class ActionHandler:
    """
    Handles execution of actions from AI model output.

    Args:
        confirmation_callback: Optional callback for sensitive action confirmation.
            Should return True to proceed, False to cancel.
        takeover_callback: Optional callback for takeover requests (login, captcha).
    """

    def __init__(
        self,
        confirmation_callback: Optional[Callable[[str], bool]] = None,
        takeover_callback: Optional[Callable[[str], None]] = None,
    ):
        self.confirmation_callback = confirmation_callback or self._default_confirmation
        self.takeover_callback = takeover_callback or self._default_takeover

    def execute(
        self, action: Dict[str, Any], screen_width: int, screen_height: int
    ) -> ActionResult:
        """
        Execute an action from the AI model.

        Args:
            action: The action dictionary from the model.
            screen_width: Current screen width in pixels.
            screen_height: Current screen height in pixels.

        Returns:
            ActionResult indicating success and whether to finish.
        """
        action_type = action.get("_metadata")

        if action_type == "finish":
            return ActionResult(
                success=True, should_finish=True, message=action.get("message")
            )

        if action_type != "do":
            return ActionResult(
                success=False,
                should_finish=True,
                message=f"Unknown action type: {action_type}",
            )

        action_name = action.get("action")
        handler_method = self._get_handler(action_name)

        if handler_method is None:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Unknown action: {action_name}",
            )

        try:
            return handler_method(action, screen_width, screen_height)
        except Exception as e:
            return ActionResult(
                success=False, should_finish=False, message=f"Action failed: {e}"
            )

    def _get_handler(self, action_name: str) -> Optional[Callable]:
        """Get the handler method for an action."""
        handlers = {
            "Launch": self._handle_launch,
            "Tap": self._handle_tap,
            "Type": self._handle_type,
            "Type_Name": self._handle_type,
            "Swipe": self._handle_swipe,
            "Back": self._handle_back,
            "Home": self._handle_home,
            "Double Tap": self._handle_double_tap,
            "Long Press": self._handle_long_press,
            "Wait": self._handle_wait,
            "Take_over": self._handle_takeover,
            "Note": self._handle_note,
            "Call_API": self._handle_call_api,
            "Interact": self._handle_interact,
        }
        return handlers.get(action_name)

    def _convert_relative_to_absolute(
        self, element: Union[List[int], str], screen_width: int, screen_height: int
    ) -> Tuple[int, int]:
        """Convert relative coordinates (0-1000) to absolute pixels."""
        if isinstance(element, str):
            try:
                # Handle string encoded lists like "[495, 109]"
                import ast
                element = ast.literal_eval(element)
            except Exception:
                # Fallback: try simple string splitting if literal_eval fails
                try:
                    clean_el = element.strip('[]() ')
                    element = [int(i.strip()) for i in clean_el.split(',')]
                except Exception:
                    raise ValueError(f"Invalid coordinate format: {element}")

        if not isinstance(element, (list, tuple)) or len(element) < 2:
            raise ValueError(f"Coordinates must be a list/tuple of at least 2 numbers, got: {element}")

        x = int(float(element[0]) / 1000 * screen_width)
        y = int(float(element[1]) / 1000 * screen_height)
        return x, y

    def _handle_launch(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle app launch action."""
        app_name = action.get("app")
        if not app_name:
            return ActionResult(False, False, "No app name specified")

        success = launch_app(app_name)
        if success:
            return ActionResult(True, False)
        return ActionResult(False, False, f"App not found: {app_name}")

    def _handle_tap(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle tap action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)

        # Check for sensitive operation
        if "message" in action:
            if not self.confirmation_callback(action["message"]):
                return ActionResult(
                    success=False,
                    should_finish=True,
                    message="User cancelled sensitive operation",
                )

        tap(x, y)
        return ActionResult(True, False)

    def _handle_type(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle text input action."""
        text = action.get("text", "")

        # Clear existing text and type new text
        # PC doesn't need ADB keyboard switching
        clear_text()
        time.sleep(0.5)

        type_text(text)
        time.sleep(0.5)

        return ActionResult(True, False)

    def _handle_swipe(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle swipe action."""
        start = action.get("start")
        end = action.get("end")

        if not start or not end:
            return ActionResult(False, False, "Missing swipe coordinates")

        start_x, start_y = self._convert_relative_to_absolute(start, width, height)
        end_x, end_y = self._convert_relative_to_absolute(end, width, height)

        swipe(start_x, start_y, end_x, end_y)
        return ActionResult(True, False)

    def _handle_back(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle back button action."""
        back()
        return ActionResult(True, False)

    def _handle_home(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle home button action."""
        home()
        return ActionResult(True, False)

    def _handle_double_tap(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle double tap action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        double_tap(x, y)
        return ActionResult(True, False)

    def _handle_long_press(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle long press action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        long_press(x, y)
        return ActionResult(True, False)

    def _handle_wait(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle wait action."""
        duration_str = action.get("duration", "1 seconds")
        try:
            duration = float(duration_str.replace("seconds", "").strip())
        except ValueError:
            duration = 1.0

        time.sleep(duration)
        return ActionResult(True, False)

    def _handle_takeover(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle takeover request (login, captcha, etc.)."""
        message = action.get("message", "User intervention required")
        self.takeover_callback(message)
        return ActionResult(True, False)

    def _handle_note(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle note action (placeholder for content recording)."""
        return ActionResult(True, False)

    def _handle_call_api(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle API call action (placeholder for summarization)."""
        return ActionResult(True, False)

    def _handle_interact(self, action: Dict, width: int, height: int) -> ActionResult:
        """Handle interaction request (user choice needed)."""
        return ActionResult(True, False, message="User interaction required")

    @staticmethod
    def _default_confirmation(message: str) -> bool:
        """Default confirmation callback using console input."""
        response = input(f"Sensitive operation: {message}\nConfirm? (Y/N): ")
        return response.upper() == "Y"

    @staticmethod
    def _default_takeover(message: str) -> None:
        """Default takeover callback using console input."""
        input(f"{message}\nPress Enter after completing manual operation...")


def parse_action(response: str) -> Dict[str, Any]:
    """
    Parse action from model response.

    Args:
        response: Raw response string from the model.

    Returns:
        Parsed action dictionary.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    try:
        response = response.strip()
        
        # 0. Handle empty response
        if not response:
            return do(action="Wait", duration="1 seconds", message="Empty action received, waiting for next turn.")
            
        # 1. Clean trailing punctuation
        for punct in ["。", ".", "!", "！"]:
            if response.endswith(punct):
                response = response[:-1].strip()
        
        # 2. Isolate the FIRST function call
        if response.startswith("do("):
            idx = response.find(")")
            if idx != -1:
                response = response[:idx+1]
        elif response.startswith("finish("):
            idx = response.find(")")
            if idx != -1:
                response = response[:idx+1]

        # 3. Handle 'do' actions
        if response.startswith("do"):
            try:
                action = eval(response, {"do": do, "finish": finish})
            except (SyntaxError, NameError):
                # Fallback: if eval fails but it looks like do(...), try a safe Wait
                return do(action="Wait", duration="1 seconds", message=f"Malformed do action: {response}")
                
        # 4. Handle 'finish' actions
        elif response.startswith("finish"):
            if "message=" in response or (response.count('"') >= 2 or response.count("'") >= 2):
                try:
                    action = eval(response, {"do": do, "finish": finish})
                except (SyntaxError, NameError):
                    action = finish(message=response.replace("finish(", "").rstrip(")"))
            else:
                msg = response.replace("finish(", "").strip()
                if msg.endswith(")"):
                    msg = msg[:-1]
                action = finish(message=msg.strip("'\""))
        else:
            # Final fallback: return a Wait action with the raw content as a note
            return do(action="Wait", duration="2 seconds", message=f"Unrecognized format: {response}")
            
        return action
    except Exception as e:
        # Instead of raising, return a Wait so the loop continues
        return do(action="Wait", duration="2 seconds", message=f"Parse error: {str(e)}")


def do(**kwargs) -> Dict[str, Any]:
    """Helper function for creating 'do' actions."""
    kwargs["_metadata"] = "do"
    return kwargs


def finish(**kwargs) -> Dict[str, Any]:
    """Helper function for creating 'finish' actions."""
    kwargs["_metadata"] = "finish"
    return kwargs
