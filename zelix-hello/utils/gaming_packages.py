"""Common gaming runtimes and graphics libraries for Arch based systems."""

from pathlib import Path


RUNTIME_PACKAGES = (
    "alsa-plugins",
    "lib32-alsa-plugins",
    "lib32-libpulse",
    "giflib",
    "glfw",
    "gst-plugins-base-libs",
    "lib32-gtk3",
    "libjpeg-turbo",
    "lib32-libjpeg-turbo",
    "libva",
    "lib32-libva",
    "libxslt",
    "mpg123",
    "ocl-icd",
    "lib32-ocl-icd",
    "openal",
    "ttf-liberation",
    "lib32-gnutls",
    "wine-gecko",
    "wine-mono",
    "umu-launcher",
    "flatpak",
)


def graphics_packages(installed, devices_root=Path("/sys/bus/pci/devices")):
    """Select userspace Vulkan packages for detected display adapters.

    Kernel drivers are deliberately handled by the Drivers page. NVIDIA's
    32-bit userspace package is added only when its matching 64-bit package is
    already installed.
    """
    vendors = set()
    try:
        devices = list(Path(devices_root).iterdir())
    except OSError:
        return []
    for device in devices:
        try:
            device_class = int((device / "class").read_text().strip(), 16)
            if device_class >> 16 != 0x03:
                continue
            vendors.add(int((device / "vendor").read_text().strip(), 16))
        except (OSError, ValueError):
            continue

    packages = []
    if 0x1002 in vendors:
        packages.extend(("mesa", "lib32-mesa", "vulkan-radeon", "lib32-vulkan-radeon"))
    if 0x8086 in vendors:
        packages.extend(("mesa", "lib32-mesa", "vulkan-intel", "lib32-vulkan-intel"))
    if 0x10DE in vendors:
        if "nvidia-utils" in installed:
            packages.append("lib32-nvidia-utils")
        elif "vulkan-nouveau" in installed:
            packages.extend(("mesa", "lib32-mesa", "lib32-vulkan-nouveau"))
    return list(dict.fromkeys(packages))
