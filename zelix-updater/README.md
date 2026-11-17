# Zelix Updater

A system update application for ZelixOS, written in Python and PyQt6. It checks configured pacman repositories for updates and displays the operation output.

## Installation

On a system with the Zelix package repository configured:

```bash
sudo pacman -Syu zelix-updater
zelix-updater
```

## Usage

Check for updates, then start the system update. Updating requests administrator privileges through `pkexec` and runs `pacman -Syu --noconfirm`. Pacman prompts use their default answers.

AUR and Flatpak updates are outside this application's scope.

## Running from source

Requires Python, `python-pyqt6`, `polkit`, `pacman-contrib`, and `fakeroot`. A Polkit authentication agent must be available in the graphical session.

```bash
python main.py
```

Update checks use `checkupdates`. The application icon and desktop entry are included in the source directory.

The package recipe is maintained in [zelix-repo](https://github.com/ZelixOS/zelix-repo/tree/main/zelix-updater).
