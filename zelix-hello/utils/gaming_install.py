"""Install the gaming bundle and preserve an unowned ZelixOS release file."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


LSB_RELEASE = Path("/etc/lsb-release")


def install(packages, release_file=LSB_RELEASE):
    if os.geteuid() != 0:
        raise PermissionError("Gaming package installation must run through sudo")
    if not packages:
        raise ValueError("No packages were provided")

    release_file = Path(release_file)
    backup = None
    if "steam" in packages and os.path.lexists(release_file):
        owner = subprocess.run(
            ["pacman", "-Qoq", "--", str(release_file)],
            capture_output=True, text=True, check=False,
        )
        if owner.returncode != 0:
            if release_file.is_symlink() or not release_file.is_file():
                raise RuntimeError(f"Review the unexpected file before installing Steam: {release_file}")
            backup = release_file.with_name(
                f"{release_file.name}.zelix-hello-backup-{time.time_ns()}-{os.getpid()}"
            )
            release_file.rename(backup)
            print(f"Preserved the unowned release file at {backup}", flush=True)

    try:
        return subprocess.call(
            ["pacman", "-Syu", "--needed", "--noconfirm", "--", *packages]
        )
    finally:
        if backup is not None:
            shutil.copy2(backup, release_file)
            print(f"Restored ZelixOS release information from {backup}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "--":
        raise SystemExit("Usage: gaming_install.py -- PACKAGE [PACKAGE ...]")
    raise SystemExit(install(sys.argv[2:]))
