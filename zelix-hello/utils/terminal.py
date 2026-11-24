"""Launch commands in the terminal preferred by the current desktop."""

import os
import shlex
import shutil
import subprocess
from pathlib import Path


EXEC_ARGUMENTS = {
    "alacritty": ["-e"],
    "konsole": ["-e"],
    "gnome-terminal": ["--wait", "--"],
    "kgx": ["--"],
    "xfce4-terminal": ["--disable-server", "--command"],
    "kitty": ["--"],
    "foot": ["-e"],
    "xterm": ["-e"],
    "wezterm": ["start", "--"],
}


def _known_terminal(value, command):
    try:
        parts = shlex.split(value)
    except ValueError:
        return None
    if not parts or not shutil.which(parts[0]):
        return None
    name = os.path.basename(parts[0])
    arguments = EXEC_ARGUMENTS.get(name)
    if arguments is None:
        return None
    if name == "xfce4-terminal":
        return [*parts, *arguments, shlex.join(command)]
    return [*parts, *arguments, *command]


def _xdg_choice_configured(desktops):
    config_home = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    config_dirs = os.environ.get("XDG_CONFIG_DIRS", "/etc/xdg").split(":")
    data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
    locations = [Path(config_home), *(Path(d) for d in config_dirs)]
    locations += [Path(d) / "xdg-terminal-exec" for d in data_dirs]
    names = [*(f"{desktop}-xdg-terminals.list" for desktop in desktops if desktop),
             "xdg-terminals.list"]
    return any((directory / name).is_file() for directory in locations for name in names)


def terminal_launch_command(command):
    """Return an argv that runs *command* in the user's preferred terminal."""
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").casefold().split(":")

    configured = os.environ.get("TERMINAL", "")
    if configured:
        launch = _known_terminal(configured, command)
        if launch:
            return launch

    if "kde" in desktop and shutil.which("kreadconfig6"):
        try:
            result = subprocess.run(
                ["kreadconfig6", "--file", "kdeglobals", "--group", "General",
                 "--key", "TerminalApplication"],
                capture_output=True, text=True, timeout=3, check=False,
            )
            if result.returncode == 0:
                launch = _known_terminal(result.stdout.strip(), command)
                if launch:
                    return launch
        except (OSError, subprocess.TimeoutExpired):
            pass

    if shutil.which("xdg-terminal-exec") and _xdg_choice_configured(desktop):
        return ["xdg-terminal-exec", "--", *command]

    preferred = {
        "kde": ["konsole"],
        "gnome": ["kgx", "gnome-terminal"],
        "xfce": ["xfce4-terminal"],
        "sway": ["foot"],
        "hyprland": ["kitty", "foot"],
    }
    candidates = [name for key in desktop for name in preferred.get(key, [])]
    for name in candidates:
        launch = _known_terminal(name, command)
        if launch:
            return launch
    if shutil.which("xdg-terminal-exec"):
        return ["xdg-terminal-exec", "--", *command]
    for name in EXEC_ARGUMENTS:
        launch = _known_terminal(name, command)
        if launch:
            return launch
    return None
