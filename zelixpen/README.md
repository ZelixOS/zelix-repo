# ZelixPen

An on-screen drawing and annotation tool written in Python and PyQt6.

## Features

- Freehand drawing, lines, arrows, rectangles, and circles.
- Color and pen width selection.
- Undo, redo, and clear actions.
- Pointer mode for interacting with applications underneath.
- Export drawings as PNG images with transparent backgrounds.

## Installation

On a system with the Zelix package repository configured:

```bash
sudo pacman -Syu zelixpen
zelixpen
```

## Running from source

Requires Python and `python-pyqt6`:

```bash
python main.py
```

Select a drawing tool from the toolbar. Switch to pointer mode to interact with the desktop; select a drawing tool to resume drawing. Window layering and pointer behavior depend on the desktop session.

The package recipe is maintained in [zelix-repo](https://github.com/ZelixOS/zelix-repo/tree/main/zelixpen).

## Languages

English, Turkish, and Spanish are supported. Use the language selector to change the interface; the choice is saved for future sessions. The initial language follows `LC_ALL`, `LC_MESSAGES`, then `LANG`. External command output and native dialogs can follow the system locale.
