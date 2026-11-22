# Zelix CLI

A command-line management tool for ZelixOS, written in Bash. It provides system updates, maintenance commands, and access to companion applications.

## Installation

On a system with the Zelix package repository configured:

```bash
sudo pacman -Syu zelix-cli
zelix help
```

## Commands

| Command | Action |
| --- | --- |
| `zelix update` | Update the system, using an available AUR helper, and Flatpak |
| `zelix mirrors` | Configure package mirrors |
| `zelix clean` | Maintain the package cache and orphaned packages |
| `zelix flathub` | Configure Flathub support |
| `zelix info` | Display system information |
| `zelix hello` | Open Zelix Hello |
| `zelix lang tr` | Use the Turkish interface |
| `zelix lang en` | Use the English interface |
| `zelix lang es` | Use the Spanish interface |

## Dependencies

Requires Bash, pacman, and sudo. Depending on the command, Flatpak, rate-mirrors, fastfetch, Paru, Yay, or Zelix Hello may also be needed. The language preference is stored in `zelix/cli.conf` under the XDG configuration directory, which defaults to `~/.config/zelix/cli.conf`.

## Running from source

```bash
bash zelix help
```

Build the package as a regular user with `makepkg -s`.
