import subprocess

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt

from utils.command_runner import CommandRunner
from utils.translations import Translator


class TweaksTab(QWidget):
    SERVICES = (
        ("bluetooth", "bluetooth.service", "tw_bt", "tw_bt_desc"),
        ("firewall", "ufw.service", "tw_fw", "tw_fw_desc"),
        ("trim", "fstrim.timer", "tw_trim", "tw_trim_desc"),
        ("printing", "cups.service", "tw_printing", "tw_printing_desc"),
    )

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.runner = None
        self.service_rows = {}
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
        self.refresh_button.clicked.connect(self.refresh_service_statuses)
        header.addWidget(self.refresh_button)
        layout.addLayout(header)

        self.title = QLabel()
        self.title.setObjectName("title_label")
        layout.addWidget(self.title)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("page_description")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        self.services_title = QLabel()
        self.services_title.setObjectName("section_title")
        layout.addWidget(self.services_title)

        self.service_table = QTableWidget(len(self.SERVICES), 3)
        self.service_table.setObjectName("service_table")
        self.service_table.verticalHeader().setVisible(False)
        self.service_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.service_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.service_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.service_table.setShowGrid(False)
        self.service_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.service_table.horizontalHeader().setFixedHeight(38)
        self.service_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.service_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.service_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.service_table.setColumnWidth(1, 130)
        self.service_table.setColumnWidth(2, 150)
        self.service_table.setFixedHeight(38 + len(self.SERVICES) * 64 + 2)

        for row_index, (key, unit, title_key, description_key) in enumerate(self.SERVICES):
            self.service_table.setRowHeight(row_index, 64)
            text_widget = QWidget()
            text_layout = QVBoxLayout(text_widget)
            text_layout.setContentsMargins(10, 6, 10, 6)
            text_layout.setSpacing(2)
            name_label = QLabel()
            name_label.setObjectName("service_name")
            description_label = QLabel()
            description_label.setObjectName("service_description")
            description_label.setWordWrap(True)
            text_layout.addWidget(name_label)
            text_layout.addWidget(description_label)

            status_label = QLabel()
            status_label.setObjectName("service_status")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(8, 6, 8, 6)
            action_button = QPushButton()
            action_button.setFixedSize(126, 40)
            action_button.clicked.connect(
                lambda _checked=False, service_key=key: self.toggle_service(service_key)
            )
            action_layout.addStretch()
            action_layout.addWidget(action_button)

            self.service_table.setCellWidget(row_index, 0, text_widget)
            self.service_table.setCellWidget(row_index, 1, status_label)
            self.service_table.setCellWidget(row_index, 2, action_widget)
            self.service_rows[key] = {
                "unit": unit,
                "title_key": title_key,
                "description_key": description_key,
                "name": name_label,
                "description": description_label,
                "status": status_label,
                "button": action_button,
                "available": False,
                "active": False,
            }

        layout.addWidget(self.service_table)

        self.note = QLabel()
        self.note.setObjectName("muted_label")
        self.note.setWordWrap(True)
        layout.addWidget(self.note)

        self.result_label = QLabel()
        self.result_label.setObjectName("service_result")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        layout.addStretch()

        self.retranslate_ui()

    @staticmethod
    def _service_state(unit):
        try:
            result = subprocess.run(
                ["systemctl", "list-unit-files", unit, "--no-legend", "--no-pager"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            available = any(line.split() and line.split()[0] == unit for line in result.stdout.splitlines())
            if not available:
                return False, False
            active = subprocess.run(
                ["systemctl", "is-active", "--quiet", unit],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
            ).returncode == 0
            return True, active
        except (OSError, subprocess.TimeoutExpired):
            return False, False

    def refresh_service_statuses(self):
        for row in self.service_rows.values():
            available, active = self._service_state(row["unit"])
            row["available"] = available
            row["active"] = active
            self._update_service_row(row)

    def _update_service_row(self, row):
        status_label = row["status"]
        button = row["button"]
        if not row["available"]:
            state = "unavailable"
            status_label.setText(Translator.get("status_unavailable"))
            button.setText(Translator.get("tw_not_installed"))
            button.setEnabled(False)
        elif row["active"]:
            state = "active"
            status_label.setText(Translator.get("status_active"))
            button.setText(Translator.get("tw_disable"))
            button.setEnabled(self.runner is None)
        else:
            state = "inactive"
            status_label.setText(Translator.get("status_inactive"))
            button.setText(Translator.get("tw_enable"))
            button.setEnabled(self.runner is None)
        status_label.setProperty("state", state)
        status_label.style().unpolish(status_label)
        status_label.style().polish(status_label)

    def _set_controls_enabled(self, enabled):
        self.refresh_button.setEnabled(enabled)
        for row in self.service_rows.values():
            row["button"].setEnabled(enabled and row["available"])

    def toggle_service(self, service_key):
        row = self.service_rows[service_key]
        if not row["available"] or self.runner is not None:
            return
        if service_key == "firewall" and row["active"]:
            answer = QMessageBox.question(
                self,
                Translator.get("confirm_title"),
                Translator.get("tw_firewall_disable_confirm"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        action = "disable" if row["active"] else "enable"
        command = ["systemctl", action, "--now", row["unit"]]
        self.result_label.setText(Translator.get("status_running"))
        self._set_controls_enabled(False)
        self.runner = CommandRunner(command, use_pkexec=True)
        self.runner.finished_signal.connect(
            lambda return_code, key=service_key: self._service_finished(key, return_code)
        )
        self.runner.start()

    def _service_finished(self, service_key, return_code):
        self.runner = None
        self.refresh_service_statuses()
        self._set_controls_enabled(True)
        if return_code == 0:
            name = self.service_rows[service_key]["name"].text()
            self.result_label.setText(
                Translator.get("tw_service_updated").format(service=name)
            )
        else:
            self.result_label.setText(
                Translator.get("tw_service_failed").format(code=return_code)
            )

    def retranslate_ui(self):
        self.btn_back.setText(Translator.get("btn_back"))
        self.refresh_button.setText(Translator.get("tw_refresh"))
        self.title.setText(Translator.get("tw_title"))
        self.subtitle.setText(Translator.get("tw_subtitle"))
        self.services_title.setText(Translator.get("tw_services"))
        self.service_table.setHorizontalHeaderLabels((
            Translator.get("tw_service_column"),
            Translator.get("tw_status_column"),
            Translator.get("tw_action_column"),
        ))
        self.service_table.horizontalHeaderItem(0).setTextAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        for column in (1, 2):
            self.service_table.horizontalHeaderItem(column).setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )
        self.note.setText(Translator.get("tw_note"))
        for row in self.service_rows.values():
            row["name"].setText(Translator.get(row["title_key"]))
            row["description"].setText(Translator.get(row["description_key"]))
        self.refresh_service_statuses()
