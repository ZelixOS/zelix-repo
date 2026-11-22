# ZelixOS Package Repository

Package recipes, packaging sources, and pacman repository indexes for ZelixOS applications.

![ZelixRepo package publishing flow](docs/images/zelixrepo-packages.svg)

This repository publishes stable ZelixOS packages and the indexes pacman uses to find them. Application sources remain in their own repositories; package build recipes and repository metadata are maintained here.

## Packages

| Directory | Contents |
| --- | --- |
| `zelix-hello/` | Welcome and system management application |
| `zelix-updater/` | System update application |
| `zelixins/` | Graphical installer |
| `zelix-cli/` | Command-line management tool |
| `zelixpen/` | Standalone drawing tool for a separate ZelixOS project |
| `paru/`, `yay/` | AUR helper package recipes |
| `x86_64/` | Repository database and file index |

## Installation

On ZelixOS with the `zelixrepo` repository configured:

```bash
sudo pacman -Syu zelix-hello zelix-updater zelix-cli
```

Package archives and repository indexes are distributed through the [stable release](https://github.com/ZelixOS/zelix-repo/releases/tag/stable). Large package archives are stored as release assets rather than in the Git source tree.

## Building packages

Use Arch Linux or ZelixOS with `base-devel` and the dependencies listed in the relevant PKGBUILD. Run this command as a regular user from the package directory:

```bash
makepkg -s
```

In the ZelixOS development workspace, application sources are synchronized from their main directories. Edit application code there and package recipes in this repository.

## Indexing and publishing

Use `repo-add` to generate an index of the packages being published. Upload package archives and SHA256 files first. Verify that every indexed package exists on GitHub and matches its indexed SHA256 before publishing these files:

- `zelixrepo.db` and `zelixrepo.db.tar.gz`
- `zelixrepo.files` and `zelixrepo.files.tar.gz`

The manually triggered `Publish Zelixins` GitHub Actions workflow builds and publishes the installer package only.
