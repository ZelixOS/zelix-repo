# Zelix Hello

A welcome and system management application for ZelixOS, written in Python and PyQt6.

## Features

- System information and project links.
- Application management through Arch repositories, Flatpak, and the AUR.
- Access to update, mirror, and maintenance tools.
- System service and desktop settings.
- Hardware detection and driver suggestions.
- English and Turkish interface.

## Installation

On a system with the Zelix package repository configured:

```bash
sudo pacman -Syu zelix-hello
zelix-hello
```

## Running from source

Requires Python, `python-pyqt6`, `qt6-svg`, and `polkit`. From the project directory:

```bash
python main.py
```

Flatpak, AUR, and mirror operations require their respective tools. Privileged operations use the desktop authentication agent.

## Source structure

`tabs/` contains application pages, `ui/` contains the main window and styles, `utils/` contains helpers and translations, and `assets/` contains images and icons.

The package recipe is maintained in [zelix-repo](https://github.com/ZelixOS/zelix-repo/tree/main/zelix-hello).
