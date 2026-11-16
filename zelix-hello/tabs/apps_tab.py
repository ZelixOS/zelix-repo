import re
import shlex
import shutil
import subprocess

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QAbstractItemView, QCheckBox, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget,
)

from utils.translations import Translator


class AppsTab(QWidget):
    """Install optional applications from one searchable list."""

    CATEGORIES = [
        ("cat_browsers", [
            ("Firefox", "firefox", "arch"),
            ("Chromium", "chromium", "arch"),
            ("Falkon", "falkon", "arch"),
            ("Tor Browser Launcher", "torbrowser-launcher", "arch"),
            ("Brave", "brave-bin", "aur"),
            ("LibreWolf", "librewolf", "arch"),
            ("Helium", "helium-browser-bin", "aur"),
        ]),
        ("cat_communication", [
            ("Thunderbird", "thunderbird", "arch"),
            ("Discord", "discord", "arch"),
            ("Telegram Desktop", "telegram-desktop", "arch"),
            ("qBittorrent", "qbittorrent", "arch"),
            ("Signal Desktop", "signal-desktop", "arch"),
            ("Element", "element-desktop", "arch"),
        ]),
        ("cat_gaming", [
            ("Steam", "steam", "arch"),
            ("Lutris", "lutris", "arch"),
            ("Wine", "wine", "arch"),
            ("Winetricks", "winetricks", "arch"),
            ("GameMode", "gamemode", "arch"),
            ("MangoHud", "mangohud", "arch"),
            ("ProtonUp-Qt", "net.davidotek.pupgui2", "flatpak"),
        ]),
        ("cat_terminals", [
            ("Alacritty", "alacritty", "arch"),
            ("Kitty", "kitty", "arch"),
            ("Foot", "foot", "arch"),
            ("Neovim", "neovim", "arch"),
            ("Helix", "helix", "arch"),
            ("Kate", "kate", "arch"),
        ]),
        ("cat_devtools", [
            ("Code (OSS)", "code", "arch"),
            ("Git", "git", "arch"),
            ("Base-devel", "base-devel", "arch"),
            ("Python", "python", "arch"),
            ("Node.js", "nodejs", "arch"),
            ("Docker", "docker", "arch"),
        ]),
        ("cat_editing", [
            ("VLC", "vlc", "arch"),
            ("GIMP", "gimp", "arch"),
            ("OBS Studio", "obs-studio", "arch"),
            ("Audacity", "audacity", "arch"),
            ("Kdenlive", "kdenlive", "arch"),
            ("Spotify", "com.spotify.Client", "flatpak"),
            ("MPV", "mpv", "arch"),
        ]),
        ("cat_graphics", [
            ("Inkscape", "inkscape", "arch"),
            ("Krita", "krita", "arch"),
            ("Blender", "blender", "arch"),
        ]),
        ("cat_office", [
            ("LibreOffice", "libreoffice-fresh", "arch"),
            ("Okular", "okular", "arch"),
            ("Evince", "evince", "arch"),
        ]),
        ("cat_utilities", [
            ("Flameshot", "flameshot", "arch"),
            ("KeePassXC", "keepassxc", "arch"),
            ("FileZilla", "filezilla", "arch"),
            ("Remmina", "remmina", "arch"),
            ("Syncthing", "syncthing", "arch"),
        ]),
        ("cat_system", [
            ("Timeshift", "timeshift", "arch"),
            ("Htop", "htop", "arch"),
            ("Btop", "btop", "arch"),
            ("Fastfetch", "fastfetch", "arch"),
            ("Flatpak", "flatpak", "arch"),
            ("GParted", "gparted", "arch"),
        ]),
        ("cat_aur", [
            ("Yay", "yay", "aur"),
            ("Paru", "paru", "aur"),
        ]),
    ]

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.package_items = {}
        self.package_data = {}
        self.category_items = {}
        self.category_packages = {}
        self.installed_arch = set()
        self.installed_flatpak = set()
        self.install_process = None
        self.pending_packages = []
        self._updating_tree = False
        self._init_ui()
        Translator.add_listener(self)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(10)

        header = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.setObjectName("back_btn")
        self.btn_back.clicked.connect(lambda: self.parent_window.navigate_to(0))
        header.addWidget(self.btn_back)
        header.addStretch()
        layout.addLayout(header)

        self.title = QLabel()
        self.title.setObjectName("title_label")
        layout.addWidget(self.title)

        self.description = QLabel()
        self.description.setObjectName("page_description")
        self.description.setWordWrap(True)
        layout.addWidget(self.description)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._filter_packages)
        layout.addWidget(self.search_input)

        self.package_tree = QTreeWidget()
        self.package_tree.setObjectName("package_tree")
        self.package_tree.setColumnCount(1)
        self.package_tree.setHeaderHidden(True)
        self.package_tree.setIndentation(20)
        self.package_tree.setRootIsDecorated(True)
        self.package_tree.setUniformRowHeights(True)
        self.package_tree.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.package_tree, 1)

        for category_key, packages in self.CATEGORIES:
            category_item = QTreeWidgetItem(self.package_tree)
            category_item.setFlags(
                category_item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            category_item.setCheckState(0, Qt.CheckState.Unchecked)
            font = category_item.font(0)
            font.setBold(True)
            category_item.setFont(0, font)
            self.category_items[category_key] = category_item
            self.category_packages[category_key] = []

            for name, package, source in packages:
                item = QTreeWidgetItem(category_item)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)
                self.package_items[package] = item
                self.package_data[package] = {
                    "name": name,
                    "source": source,
                    "category": category_key,
                }
                self.category_packages[category_key].append(package)

        self.category_items["cat_browsers"].setExpanded(True)

        options = QHBoxLayout()
        self.multilib_check = QCheckBox()
        self.multilib_check.setEnabled(False)
        options.addWidget(self.multilib_check)
        options.addStretch()
        self.count_label = QLabel()
        self.count_label.setObjectName("muted_label")
        options.addWidget(self.count_label)
        layout.addLayout(options)

        actions = QHBoxLayout()
        actions.addStretch()
        self.install_button = QPushButton()
        self.install_button.setObjectName("primary_btn")
        self.install_button.clicked.connect(self.install_selected)
        actions.addWidget(self.install_button)
        layout.addLayout(actions)

        self.process_timer = QTimer(self)
        self.process_timer.setInterval(750)
        self.process_timer.timeout.connect(self._check_install_process)

        self.package_tree.itemChanged.connect(self._item_changed)
        self.refresh_installed_packages()
        self.retranslate_ui()

    @staticmethod
    def _command_output(command):
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=10, check=False
            )
            return set(result.stdout.splitlines()) if result.returncode == 0 else set()
        except (OSError, subprocess.TimeoutExpired):
            return set()

    def refresh_installed_packages(self):
        self.installed_arch = self._command_output(["pacman", "-Qq"])
        if shutil.which("flatpak"):
            self.installed_flatpak = self._command_output(
                ["flatpak", "list", "--app", "--columns=application"]
            )
        else:
            self.installed_flatpak = set()
        self._refresh_package_items()

    def _is_installed(self, package):
        source = self.package_data[package]["source"]
        installed = self.installed_flatpak if source == "flatpak" else self.installed_arch
        return package in installed

    def _refresh_package_items(self):
        self._updating_tree = True
        installed_text = Translator.get("apps_installed")
        for package, item in self.package_items.items():
            data = self.package_data[package]
            installed = self._is_installed(package)
            item.setText(0, f"{data['name']} ({installed_text})" if installed else data["name"])
            item.setToolTip(0, f"{package} - {self._source_name(data['source'])}")
            if installed:
                item.setCheckState(0, Qt.CheckState.Unchecked)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            else:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self._updating_tree = False
        self._refresh_category_states()
        self._update_selection()

    def _source_name(self, source):
        return Translator.get(f"apps_source_{source}")

    def _is_selected(self, package):
        return self.package_items[package].checkState(0) == Qt.CheckState.Checked

    def _item_changed(self, item, _column):
        if self._updating_tree:
            return
        if item.parent() is None and item.checkState(0) != Qt.CheckState.PartiallyChecked:
            self._updating_tree = True
            for index in range(item.childCount()):
                child = item.child(index)
                package = self._package_for_item(child)
                if package and not self._is_installed(package):
                    child.setCheckState(0, item.checkState(0))
            self._updating_tree = False
        self._refresh_category_states()
        self._update_selection()

    def _package_for_item(self, item):
        for package, package_item in self.package_items.items():
            if package_item is item:
                return package
        return None

    def _refresh_category_states(self):
        self._updating_tree = True
        for category_key, category_item in self.category_items.items():
            packages = self.category_packages[category_key]
            available = [package for package in packages if not self._is_installed(package)]
            selected = sum(self._is_selected(package) for package in available)
            if not selected:
                state = Qt.CheckState.Unchecked
            elif selected == len(available):
                state = Qt.CheckState.Checked
            else:
                state = Qt.CheckState.PartiallyChecked
            category_item.setCheckState(0, state)
            category_item.setText(
                0, f"{Translator.get(category_key)}   {selected}/{len(available)}"
            )
        self._updating_tree = False

    def _filter_packages(self, _text=""):
        query = self.search_input.text().strip().casefold()
        for category_key, category_item in self.category_items.items():
            category_visible = False
            for package in self.category_packages[category_key]:
                name = self.package_data[package]["name"]
                visible = not query or query in f"{name} {package}".casefold()
                self.package_items[package].setHidden(not visible)
                category_visible = category_visible or visible
            category_item.setHidden(not category_visible)
            if query and category_visible:
                category_item.setExpanded(True)

    def selected_packages(self):
        return [
            package for package in self.package_items
            if self._is_selected(package) and not self._is_installed(package)
        ]

    def _update_selection(self):
        selected = self.selected_packages()
        self.count_label.setText(
            Translator.get("apps_selected_count").format(count=len(selected))
        )
        self.install_button.setEnabled(bool(selected) and self.install_process is None)
        self.multilib_check.setChecked(self._multilib_enabled())
        self.multilib_check.setVisible("steam" in selected)

    @staticmethod
    def _multilib_enabled():
        try:
            with open("/etc/pacman.conf", "r", encoding="utf-8") as config:
                return any(re.fullmatch(r"\s*\[multilib\]\s*", line) for line in config)
        except OSError:
            return False

    @staticmethod
    def _terminal_command():
        terminals = [
            ("alacritty", ["alacritty", "-e"]),
            ("konsole", ["konsole", "-e"]),
            ("gnome-terminal", ["gnome-terminal", "--wait", "--"]),
            ("xfce4-terminal", ["xfce4-terminal", "--disable-server", "-e"]),
            ("kitty", ["kitty", "--"]),
            ("foot", ["foot", "-e"]),
            ("xterm", ["xterm", "-e"]),
        ]
        for name, command in terminals:
            if shutil.which(name):
                return command
        return None

    def _build_install_script(self, packages):
        arch = [p for p in packages if self.package_data[p]["source"] == "arch"]
        flatpak = [p for p in packages if self.package_data[p]["source"] == "flatpak"]
        aur = [p for p in packages if self.package_data[p]["source"] == "aur"]
        commands = ["set -e"]
        aur_review_prompt = shlex.quote(Translator.get("apps_aur_review_prompt"))
        if arch:
            commands.append("sudo pacman -S --needed -- " + shlex.join(arch))
        if flatpak:
            commands.append("command -v flatpak >/dev/null || sudo pacman -S --needed -- flatpak")
            commands.append("flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo")
            commands.append("flatpak install -y flathub " + shlex.join(flatpak))
        for package in aur:
            quoted = shlex.quote(package)
            candidates = [package] if package.endswith("-bin") else [f"{package}-bin", package]
            clone_commands = " || ".join(
                "git clone --depth 1 "
                + shlex.quote(f"https://aur.archlinux.org/{candidate}.git")
                + ' "$build_dir/source"'
                for candidate in candidates
            )
            commands.append(
                f"if pacman -Si -- {quoted} >/dev/null 2>&1; then "
                f"sudo pacman -S --needed -- {quoted}; else "
                f"if command -v paru >/dev/null 2>&1; then paru -S --needed -- {quoted}; "
                f"elif command -v yay >/dev/null 2>&1; then yay -S --needed -- {quoted}; "
                f"elif pacman -Si -- paru >/dev/null 2>&1; then "
                f"sudo pacman -S --needed -- paru; paru -S --needed -- {quoted}; "
                "else sudo pacman -S --needed -- base-devel git; "
                "(build_dir=$(mktemp -d); "
                "trap 'rm -rf \"$build_dir\"' EXIT; "
                f"{clone_commands}; "
                "cd \"$build_dir/source\"; "
                "printf '\\n%s\\n' " + aur_review_prompt + "; "
                "cat PKGBUILD; "
                "printf '\\n[y/N]: '; read -r aur_confirm; "
                "case \"$aur_confirm\" in y|Y|e|E) ;; *) exit 1 ;; esac; "
                "makepkg -si); fi; fi"
            )
        done_text = shlex.quote(Translator.get("apps_terminal_done"))
        commands.extend([f"printf '\n%s\n' {done_text}", "read -r"])
        return "; ".join(commands)

    def install_selected(self):
        packages = self.selected_packages()
        if not packages:
            return
        if "steam" in packages and not self._multilib_enabled():
            QMessageBox.warning(
                self, Translator.get("msg_error"), Translator.get("apps_multilib_warning")
            )
            return
        names = "\n".join(f"- {self.package_data[p]['name']}" for p in packages)
        confirmation = Translator.get("apps_confirm_install").format(packages=names)
        if any(self.package_data[package]["source"] == "aur" for package in packages):
            confirmation += "\n\n" + Translator.get("apps_aur_warning")
        answer = QMessageBox.question(
            self,
            Translator.get("confirm_title"),
            confirmation,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        terminal = self._terminal_command()
        if terminal is None:
            QMessageBox.warning(
                self, Translator.get("msg_error"), Translator.get("msg_unsupported_term")
            )
            return
        try:
            script = self._build_install_script(packages)
            self.install_process = subprocess.Popen(terminal + ["bash", "-lc", script])
            self.pending_packages = list(packages)
        except OSError as error:
            self.install_process = None
            self.pending_packages = []
            QMessageBox.warning(
                self, Translator.get("msg_error"),
                f"{Translator.get('msg_term_fail')} {error}",
            )
            return
        self.install_button.setEnabled(False)
        self.install_button.setText(Translator.get("status_running"))
        self.process_timer.start()

    def _check_install_process(self):
        if self.install_process is None:
            self.process_timer.stop()
            return
        return_code = self.install_process.poll()
        if return_code is None:
            return
        self.process_timer.stop()
        self.install_process = None
        attempted_packages = self.pending_packages
        self.pending_packages = []
        self.refresh_installed_packages()
        self.install_button.setText(Translator.get("apps_install_selected"))
        missing_packages = [
            package for package in attempted_packages
            if not self._is_installed(package)
        ]
        if not missing_packages:
            QMessageBox.information(
                self, Translator.get("msg_success"), Translator.get("apps_install_finished")
            )
        else:
            QMessageBox.warning(
                self,
                Translator.get("msg_error"),
                Translator.get("apps_install_missing").format(
                    packages="\n".join(f"- {package}" for package in missing_packages),
                    code=return_code,
                ),
            )

    def retranslate_ui(self):
        self.btn_back.setText(Translator.get("btn_back"))
        self.title.setText(Translator.get("apps_title"))
        self.description.setText(Translator.get("apps_description"))
        self.search_input.setPlaceholderText(Translator.get("apps_search"))
        self.install_button.setText(
            Translator.get("status_running")
            if self.install_process is not None
            else Translator.get("apps_install_selected")
        )
        self.multilib_check.setText(Translator.get("apps_multilib_required"))
        self._refresh_package_items()
        self._filter_packages()
