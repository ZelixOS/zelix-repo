# Yay Package Recipe

Yay is an AUR helper for Arch Linux, written in Go. This directory contains the PKGBUILD used to distribute it through the ZelixOS package repository.

## Building

Use Arch Linux or ZelixOS with `base-devel`, Go, and the dependencies listed in the PKGBUILD. Run as a regular user:

```bash
makepkg -s
```

Sources are downloaded from the upstream URL specified in the PKGBUILD. The same file defines the package version and source checksums.

## Usage

On a system with the Zelix package repository configured:

```bash
sudo pacman -Syu yay
yay --help
```

Review AUR package recipes before installation.
