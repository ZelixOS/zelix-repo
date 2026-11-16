import os
import re
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from utils.command_runner import CommandRunner
from utils.translations import Translator


class DriversTab(QWidget):
    """Detect common hardware and install matching Arch packages."""

    NVIDIA_DRIVER_PACKAGES = {
        "nvidia", "nvidia-dkms", "nvidia-lts", "nvidia-open",
        "nvidia-open-dkms", "nvidia-open-lts",
    }

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.runner = None
        self.package_items = {}
        self.installed_packages = set()
        self._init_ui()
        Translator.add_listener(self)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.setObjectName("back_btn")
        self.btn_back.clicked.connect(lambda: self.parent_window.navigate_to(2))
        header.addWidget(self.btn_back)
        header.addStretch()
        self.refresh_button = QPushButton()
        self.refresh_button.clicked.connect(self.refresh_hardware)
        header.addWidget(self.refresh_button)
        layout.addLayout(header)

        self.title = QLabel()
        self.title.setObjectName("title_label")
        layout.addWidget(self.title)

        self.description = QLabel()
        self.description.setObjectName("page_description")
        self.description.setWordWrap(True)
        layout.addWidget(self.description)

        self.hardware_tree = QTreeWidget()
        self.hardware_tree.setObjectName("driver_tree")
        self.hardware_tree.setColumnCount(2)
        self.hardware_tree.setRootIsDecorated(True)
        self.hardware_tree.setUniformRowHeights(True)
        self.hardware_tree.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.hardware_tree.header().setStretchLastSection(True)
        self.hardware_tree.header().resizeSection(0, 390)
        self.hardware_tree.itemChanged.connect(self._selection_changed)
        layout.addWidget(self.hardware_tree, 1)

        action_layout = QHBoxLayout()
        self.selection_label = QLabel()
        self.selection_label.setObjectName("muted_label")
        action_layout.addWidget(self.selection_label)
        action_layout.addStretch()
        self.install_button = QPushButton()
        self.install_button.setObjectName("primary_btn")
        self.install_button.clicked.connect(self.install_selected)
        action_layout.addWidget(self.install_button)
        layout.addLayout(action_layout)

        self.output = QPlainTextEdit()
        self.output.setObjectName("driver_output")
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(130)
        self.output.hide()
        layout.addWidget(self.output)

        self.retranslate_ui()
        self.refresh_hardware()

    @staticmethod
    def _command_lines(command):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            return result.stdout.splitlines() if result.returncode == 0 else []
        except (OSError, subprocess.TimeoutExpired):
            return []

    @staticmethod
    def _read_file(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except OSError:
            return ""

    def _multilib_enabled(self):
        config = self._read_file("/etc/pacman.conf")
        return bool(re.search(r"(?m)^\s*\[multilib\]\s*$", config))

    def _kernel_headers(self):
        kernels = ("linux", "linux-lts", "linux-zen", "linux-hardened")
        return [f"{kernel}-headers" for kernel in kernels if kernel in self.installed_packages]

    def _hardware_profiles(self):
        profiles = []
        pci_lines = self._command_lines(["lspci", "-nn"])
        display_lines = [
            line for line in pci_lines
            if re.search(r"VGA compatible controller|3D controller|Display controller", line, re.I)
        ]

        cpu_info = self._read_file("/proc/cpuinfo").lower()
        if "genuineintel" in cpu_info:
            profiles.append((Translator.get("drivers_intel_cpu"), ["intel-ucode"], ""))
        elif "authenticamd" in cpu_info:
            profiles.append((Translator.get("drivers_amd_cpu"), ["amd-ucode"], ""))

        profiles.append((Translator.get("drivers_firmware"), ["linux-firmware"], ""))
        multilib = self._multilib_enabled()
        gpu_count = len(display_lines)

        for line in display_lines:
            device = line.split(": ", 1)[-1]
            lowered = line.lower()
            if "[10de:" in lowered or "nvidia" in lowered:
                profiles.append(self._nvidia_profile(device, gpu_count > 1))
            elif "[1002:" in lowered or "amd/ati" in lowered or "advanced micro devices" in lowered:
                packages = ["mesa", "vulkan-radeon"]
                if multilib:
                    packages.extend(["lib32-mesa", "lib32-vulkan-radeon"])
                profiles.append((device, packages, Translator.get("drivers_amd_graphics")))
            elif "[8086:" in lowered or "intel corporation" in lowered:
                packages = ["mesa", "vulkan-intel"]
                if multilib:
                    packages.extend(["lib32-mesa", "lib32-vulkan-intel"])
                profiles.append((device, packages, Translator.get("drivers_intel_graphics")))
            else:
                profiles.append((device, [], Translator.get("drivers_no_profile")))

        network_lines = [line for line in pci_lines if "network controller" in line.lower()]
        for line in network_lines:
            if "broadcom" in line.lower():
                device = line.split(": ", 1)[-1]
                profiles.append((device, [], Translator.get("drivers_broadcom_manual")))

        virtual_profile = self._virtual_machine_profile()
        if virtual_profile:
            profiles.append(virtual_profile)

        if not pci_lines:
            profiles.append((Translator.get("drivers_detection_failed"), [], ""))
        return profiles

    def _nvidia_profile(self, device, hybrid):
        installed_driver = sorted(self.NVIDIA_DRIVER_PACKAGES & self.installed_packages)
        packages = [*installed_driver, "nvidia-utils", "nvidia-settings"]
        note = Translator.get("drivers_nvidia_existing") if installed_driver else ""

        modern = re.search(
            r"\b(RTX|GTX\s*16|Quadro\s+RTX|Tesla\s+T[4-9]|NVIDIA\s+[ABHL]\d)",
            device,
            re.I,
        )
        if not installed_driver and modern:
            packages.insert(0, "nvidia-open-dkms")
            packages.extend(self._kernel_headers())
            note = Translator.get("drivers_nvidia_modern")
        elif not installed_driver:
            packages = []
            note = Translator.get("drivers_nvidia_manual")

        if packages and self._multilib_enabled():
            packages.append("lib32-nvidia-utils")
        if packages and hybrid:
            packages.append("nvidia-prime")
        return device, packages, note

    def _virtual_machine_profile(self):
        identity = " ".join((
            self._read_file("/sys/class/dmi/id/sys_vendor"),
            self._read_file("/sys/class/dmi/id/product_name"),
        )).lower()
        if "virtualbox" in identity:
            return "VirtualBox", ["virtualbox-guest-utils"], Translator.get("drivers_virtual_guest")
        if "vmware" in identity:
            return "VMware", ["open-vm-tools"], Translator.get("drivers_virtual_guest")
        if any(name in identity for name in ("qemu", "kvm", "bochs")):
            return "QEMU/KVM", ["qemu-guest-agent", "spice-vdagent"], Translator.get("drivers_virtual_guest")
        return None

    def refresh_hardware(self):
        self.installed_packages = set(self._command_lines(["pacman", "-Qq"]))
        profiles = self._hardware_profiles()
        self.hardware_tree.blockSignals(True)
        self.hardware_tree.clear()
        self.package_items.clear()
        seen_packages = set()

        for device, packages, note in profiles:
            device_item = QTreeWidgetItem(self.hardware_tree)
            device_item.setText(0, device)
            device_item.setText(1, note)
            font = device_item.font(0)
            font.setBold(True)
            device_item.setFont(0, font)

            for package in packages:
                if package in seen_packages:
                    continue
                seen_packages.add(package)
                item = QTreeWidgetItem(device_item)
                item.setText(0, package)
                installed = package in self.installed_packages
                item.setText(
                    1,
                    Translator.get("drivers_installed")
                    if installed else Translator.get("drivers_recommended"),
                )
                if not installed:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.CheckState.Checked)
                    self.package_items[package] = item
            device_item.setExpanded(True)

        self.hardware_tree.blockSignals(False)
        self._selection_changed()

    def selected_packages(self):
        return [
            package for package, item in self.package_items.items()
            if item.checkState(0) == Qt.CheckState.Checked
        ]

    def _selection_changed(self, _item=None, _column=0):
        count = len(self.selected_packages())
        self.selection_label.setText(
            Translator.get("drivers_selected_count").format(count=count)
        )
        self.install_button.setEnabled(bool(count) and self.runner is None)

    def install_selected(self):
        packages = self.selected_packages()
        if not packages:
            return
        package_list = "\n".join(f"- {package}" for package in packages)
        answer = QMessageBox.question(
            self,
            Translator.get("confirm_title"),
            Translator.get("drivers_confirm").format(packages=package_list),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.output.clear()
        self.output.show()
        self.output.appendPlainText(Translator.get("status_running"))
        self.install_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        command = ["pacman", "-S", "--needed", "--noconfirm", "--", *packages]
        self.runner = CommandRunner(command, use_pkexec=True)
        self.runner.output_signal.connect(self.output.appendPlainText)
        self.runner.error_signal.connect(self.output.appendPlainText)
        self.runner.finished_signal.connect(self._installation_finished)
        self.runner.start()

    def _installation_finished(self, return_code):
        self.runner = None
        self.refresh_button.setEnabled(True)
        self.refresh_hardware()
        if return_code == 0:
            self.output.appendPlainText(Translator.get("drivers_install_success"))
            QMessageBox.information(
                self,
                Translator.get("msg_success"),
                Translator.get("drivers_restart_note"),
            )
        else:
            self.output.appendPlainText(
                Translator.get("drivers_install_failed").format(code=return_code)
            )

    def retranslate_ui(self):
        self.btn_back.setText(Translator.get("btn_back"))
        self.refresh_button.setText(Translator.get("drivers_refresh"))
        self.title.setText(Translator.get("drivers_title"))
        self.description.setText(Translator.get("drivers_description"))
        self.hardware_tree.setHeaderLabels((
            Translator.get("drivers_hardware_column"),
            Translator.get("drivers_status_column"),
        ))
        self.install_button.setText(Translator.get("drivers_install"))
        if self.hardware_tree.topLevelItemCount():
            self.refresh_hardware()
