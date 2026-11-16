import os
import shlex
import shutil
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QGroupBox, QMessageBox, QPlainTextEdit, QHBoxLayout,
                             QGridLayout)
from PyQt6.QtCore import Qt
from utils.command_runner import CommandRunner
from utils.translations import Translator

class SystemTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self._init_ui()
        self.runner = None
        Translator.add_listener(self)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header with back button
        header_layout = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.setObjectName("back_btn")
        self.btn_back.clicked.connect(lambda: self.parent_window.navigate_to(0))
        header_layout.addWidget(self.btn_back)
        header_layout.addStretch()
        self.btn_drivers = QPushButton()
        self.btn_drivers.clicked.connect(lambda: self.parent_window.navigate_to(4))
        header_layout.addWidget(self.btn_drivers)
        self.btn_tweaks = QPushButton()
        self.btn_tweaks.clicked.connect(lambda: self.parent_window.navigate_to(3))
        header_layout.addWidget(self.btn_tweaks)
        layout.addLayout(header_layout)

        self.title = QLabel()
        self.title.setObjectName("title_label")
        layout.addWidget(self.title)

        self.update_group = QGroupBox()
        update_layout = QHBoxLayout(self.update_group)
        update_layout.setContentsMargins(12, 18, 12, 12)
        update_layout.setSpacing(10)

        self.btn_update = QPushButton()
        self.btn_update.setObjectName("primary_btn")
        self.btn_update.clicked.connect(self.run_update)

        self.btn_updater_gui = QPushButton()
        self.btn_updater_gui.clicked.connect(self.launch_zelix_updater)

        self.btn_update.setMinimumHeight(46)
        self.btn_updater_gui.setMinimumHeight(46)
        update_layout.addWidget(self.btn_update, 1)
        update_layout.addWidget(self.btn_updater_gui, 1)

        layout.addWidget(self.update_group)

        self.maint_group = QGroupBox()
        maint_layout = QGridLayout(self.maint_group)
        maint_layout.setContentsMargins(12, 18, 12, 12)
        maint_layout.setHorizontalSpacing(10)
        maint_layout.setVerticalSpacing(10)

        self.btn_clear_cache = QPushButton()
        self.btn_clear_cache.clicked.connect(lambda: self.run_command(["pacman", "-Sc", "--noconfirm"]))

        self.btn_remove_orphans = QPushButton()
        self.btn_remove_orphans.clicked.connect(self.run_remove_orphans)

        self.btn_optimize_mirrors = QPushButton()
        self.btn_optimize_mirrors.clicked.connect(self.run_optimize_mirrors)

        self.btn_enable_flathub = QPushButton()
        self.btn_enable_flathub.clicked.connect(self.enable_flathub)

        for button in (
            self.btn_clear_cache, self.btn_remove_orphans,
            self.btn_optimize_mirrors, self.btn_enable_flathub,
        ):
            button.setMinimumHeight(44)
        maint_layout.addWidget(self.btn_clear_cache, 0, 0)
        maint_layout.addWidget(self.btn_remove_orphans, 0, 1)
        maint_layout.addWidget(self.btn_optimize_mirrors, 1, 0)
        maint_layout.addWidget(self.btn_enable_flathub, 1, 1)

        layout.addWidget(self.maint_group)

        # Terminal Output Area
        self.lbl_terminal = QLabel()
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setObjectName("terminal_output")
        self.terminal_output.setReadOnly(True)
        layout.addWidget(self.lbl_terminal)
        layout.addWidget(self.terminal_output)

        self.retranslate_ui()

    def set_buttons_enabled(self, enabled):
        self.btn_update.setEnabled(enabled)
        self.btn_updater_gui.setEnabled(enabled)
        self.btn_clear_cache.setEnabled(enabled)
        self.btn_remove_orphans.setEnabled(enabled)
        self.btn_optimize_mirrors.setEnabled(enabled)
        self.btn_enable_flathub.setEnabled(enabled)
        self.btn_drivers.setEnabled(enabled)
        self.btn_tweaks.setEnabled(enabled)

    def retranslate_ui(self):
        self.btn_back.setText(Translator.get("btn_back"))
        self.btn_drivers.setText(Translator.get("btn_drivers"))
        self.btn_tweaks.setText(Translator.get("btn_tweaks"))
        self.title.setText(Translator.get("sys_title"))
        self.update_group.setTitle(Translator.get("sys_updates"))
        self.maint_group.setTitle(Translator.get("sys_maintenance"))
        self.btn_update.setText(Translator.get("sys_update"))
        self.btn_updater_gui.setText(Translator.get("sys_updater_gui"))
        self.btn_clear_cache.setText(Translator.get("sys_clear_cache"))
        self.btn_remove_orphans.setText(Translator.get("sys_remove_orphans"))
        self.btn_optimize_mirrors.setText(Translator.get("sys_optimize_mirrors"))
        self.btn_enable_flathub.setText(Translator.get("sys_enable_flathub"))
        self.lbl_terminal.setText(Translator.get("terminal_label"))

    def log_output(self, text):
        self.terminal_output.appendPlainText(text)

    def launch_zelix_updater(self):
        if shutil.which("zelix-updater"):
            subprocess.Popen(["zelix-updater"])
        elif os.path.exists("/usr/share/zelix-updater/main.py"):
            subprocess.Popen(["python", "/usr/share/zelix-updater/main.py"])
        else:
            QMessageBox.information(
                self, "Zelix Updater", Translator.get("sys_updater_missing")
            )

    def run_update(self):
        reply = QMessageBox.question(
            self,
            Translator.get("confirm_title"),
            Translator.get("confirm_update"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.terminal_output.clear()
            self.run_command(["pacman", "-Syu", "--noconfirm"])

    def run_remove_orphans(self):
        self.terminal_output.clear()
        no_orphans = shlex.quote(Translator.get("no_orphans"))
        command = [
            "bash", "-c",
            "orphans=$(pacman -Qdtq); "
            "if [ -n \"$orphans\" ]; then "
            "echo \"$orphans\" | pkexec pacman -Rns - --noconfirm; "
            f"else echo {no_orphans}; fi"
        ]
        self.run_command(command, use_pkexec=False)

    def get_user_country(self):
        for var in ['LANG', 'LC_ADDRESS', 'LC_ALL']:
            val = os.environ.get(var)
            if val and '_' in val:
                try:
                    parts = val.split('_')
                    if len(parts) > 1:
                        country = parts[1].split('.')[0].upper()
                        if len(country) == 2 and country.isalpha():
                            return country
                except Exception:
                    pass
        return None

    def run_optimize_mirrors(self):
        if not shutil.which("rate-mirrors"):
            QMessageBox.warning(
                self,
                Translator.get("msg_error"),
                Translator.get("sys_rate_mirrors_missing")
            )
            return

        self.terminal_output.clear()
        country = self.get_user_country()
        if country:
            cmd_str = f"rate-mirrors --allow-root --entry-country {country} arch > /etc/pacman.d/mirrorlist"
        else:
            cmd_str = "rate-mirrors --allow-root arch > /etc/pacman.d/mirrorlist"

        command = ["bash", "-c", cmd_str]
        self.run_command(command, use_pkexec=True)

    def enable_flathub(self):
        self.terminal_output.clear()
        success_text = shlex.quote(Translator.get("flathub_success"))
        cmd_str = (
            "if ! command -v flatpak &>/dev/null; then pkexec pacman -S --noconfirm flatpak; fi && "
            "flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo && "
            f"echo {success_text}"
        )
        command = ["bash", "-c", cmd_str]
        self.run_command(command, use_pkexec=False)

    def run_command(self, cmd_list, use_pkexec=True):
        self.set_buttons_enabled(False)
        self.log_output(f"[{Translator.get('status_running')}]")
        self.runner = CommandRunner(cmd_list, use_pkexec=use_pkexec)
        self.runner.output_signal.connect(self.log_output)
        self.runner.error_signal.connect(self.log_output)
        self.runner.finished_signal.connect(self.on_finished)
        self.runner.start()

    def on_finished(self, rc):
        self.set_buttons_enabled(True)
        if rc == 0:
            self.log_output(f"\n[{Translator.get('msg_success')}]")
            QMessageBox.information(self, Translator.get("msg_success"), Translator.get("msg_success"))
        else:
            self.log_output(f"\n[{Translator.get('msg_error')} - Code: {rc}]")
            QMessageBox.warning(self, Translator.get("msg_error"), Translator.get("msg_error"))
