"""Enable Arch's multilib repository for the gaming setup."""

import os
from pathlib import Path
import re
import shutil
import stat
import tempfile


PACMAN_CONF = Path("/etc/pacman.conf")


def enabled_config(text):
    lines = text.splitlines(keepends=True)
    section = None
    found = False
    include_found = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
        elif stripped.startswith("#[") and stripped.endswith("]"):
            section = stripped[2:-1]
            if section == "multilib":
                lines[index] = line.replace("#[multilib]", "[multilib]", 1)
        elif section == "multilib" and re.match(r"^#?\s*Include\s*=", stripped):
            lines[index] = line.replace("#", "", 1) if stripped.startswith("#") else line
            include_found = True
        if section == "multilib":
            found = True
    if not found:
        lines.append("\n[multilib]\nInclude = /etc/pacman.d/mirrorlist\n")
    elif not include_found:
        raise ValueError("The multilib section has no mirrorlist Include directive")
    return "".join(lines)


def main():
    if os.geteuid() != 0:
        raise SystemExit("Run this helper through sudo")
    original = PACMAN_CONF.read_text(encoding="utf-8")
    updated = enabled_config(original)
    if updated == original:
        return
    backup = PACMAN_CONF.with_name("pacman.conf.zelix-hello.bak")
    if not backup.exists():
        shutil.copy2(PACMAN_CONF, backup)
    descriptor, temporary = tempfile.mkstemp(prefix="pacman.conf.", dir=PACMAN_CONF.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(updated)
        os.chmod(temporary, stat.S_IMODE(PACMAN_CONF.stat().st_mode))
        os.replace(temporary, PACMAN_CONF)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


if __name__ == "__main__":
    main()
