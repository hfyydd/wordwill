"""App name to package name mapping for supported applications."""
from typing import Optional, Union, Any, Dict, List

APP_CONFIGS: Dict[str, Dict[str, Any]] = {
    # Browsers
    "Chrome": {
        "macos": {"bundle_id": "com.google.Chrome"},
        "windows": {"executable": "chrome.exe"},
        "window_title": "Google Chrome",
    },
    "Safari": {
        "macos": {"bundle_id": "com.apple.Safari"},
        "window_title": "Safari",
    },
    "Edge": {
        "macos": {"bundle_id": "com.microsoft.edgemac"},
        "windows": {"executable": "msedge.exe"},
        "window_title": "Microsoft Edge",
    },
    # Communication
    "微信": {
        "macos": {"bundle_id": "com.tencent.xinWeChat"},
        "windows": {"executable": "WeChat.exe"},
        "window_title": "微信",
    },
    "飞书": {
        "macos": {"bundle_id": "com.electron.lark"},
        "windows": {"executable": "Lark.exe"},
        "window_title": "飞书",
    },
    "钉钉": {
        "macos": {"bundle_id": "com.alibaba.DingTalkMac"},
        "windows": {"executable": "Dingtalk.exe"},
        "window_title": "钉钉",
    },
    "QQ": {
        "macos": {"bundle_id": "com.tencent.qq"},
        "windows": {"executable": "QQ.exe"},
        "window_title": "QQ",
    },
    # Productivity
    "VS Code": {
        "macos": {"bundle_id": "com.microsoft.VSCode"},
        "windows": {"executable": "Code.exe"},
        "window_title": "Visual Studio Code",
    },
    "Obsidian": {
        "macos": {"bundle_id": "md.obsidian"},
        "windows": {"executable": "Obsidian.exe"},
        "window_title": "Obsidian",
    },
}

# Keep the legacy name for backward compatibility during transition
APP_PACKAGES = {name: cfg.get("macos", {}).get("bundle_id") or cfg.get("windows", {}).get("executable") 
                for name, cfg in APP_CONFIGS.items()}


def get_app_config(app_name: str) -> Optional[Dict]:
    """
    Get the full config for an app.

    Args:
        app_name: The display name of the app.

    Returns:
        The configuration dictionary, or None if not found.
    """
    return APP_CONFIGS.get(app_name)


def get_app_identifier(app_name: str, platform: str = "macos") -> Optional[str]:
    """
    Get the platform-specific identifier for an app.

    Args:
        app_name: The display name of the app.
        platform: The platform ('macos' or 'windows').

    Returns:
        The bundle_id (macOS) or executable (Windows), or None if not found.
    """
    cfg = get_app_config(app_name)
    if not cfg:
        return None
    
    platform_cfg = cfg.get(platform, {})
    if platform == "macos":
        return platform_cfg.get("bundle_id")
    elif platform == "windows":
        return platform_cfg.get("executable")
    return None


def get_package_name(app_name: str) -> Optional[str]:
    """
    Legacy wrapper for getting an identifier (defaults to macOS bundle_id).

    Args:
        app_name: The display name of the app.

    Returns:
        The identifier, or None if not found.
    """
    return get_app_identifier(app_name, platform="macos")


def get_app_name(identifier: str) -> Optional[str]:
    """
    Get the app name from an identifier (bundle_id or executable).

    Args:
        identifier: The platform-specific identifier.

    Returns:
        The display name of the app, or None if not found.
    """
    for name, cfg in APP_CONFIGS.items():
        # Check macOS bundle_id
        if cfg.get("macos", {}).get("bundle_id") == identifier:
            return name
        # Check Windows executable
        if cfg.get("windows", {}).get("executable") == identifier:
            return name
    return None


def list_supported_apps() -> List[str]:
    """
    Get a list of all supported app names.

    Returns:
        List of app names.
    """
    return list(APP_CONFIGS.keys())
