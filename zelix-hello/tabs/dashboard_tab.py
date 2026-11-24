import os
import shutil
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QPushButton, QGridLayout, QComboBox, QSpacerItem,
                             QSizePolicy, QDialog, QPlainTextEdit)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QIcon
from utils.translations import Translator

def get_asset_icon(name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_path = os.path.join(base_dir, "assets", "icons", name)
    if os.path.exists(local_path):
        return QIcon(local_path)
    system_path = os.path.join("/usr/share/zelix-hello/assets/icons", name)
    if os.path.exists(system_path):
        return QIcon(system_path)
    return QIcon()

class ReadmeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Translator.get("readme_title"))
        self.setMinimumSize(680, 520)
        self.resize(750, 580)
        self.current_lang = {'Turkish':'tr', 'Spanish':'es'}.get(Translator.get_language(), 'en')
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        title = QLabel(Translator.get("readme_title"))
        title.setObjectName("title_label")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.btn_lang = QPushButton()
        self.btn_lang.setObjectName("primary_btn")
        self.btn_lang.setFixedWidth(150)
        self.btn_lang.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.btn_lang)
        layout.addLayout(header_layout)

        self.text_view = QPlainTextEdit()
        self.text_view.setObjectName("readme_text")
        self.text_view.setReadOnly(True)
        layout.addWidget(self.text_view)

        bottom_layout = QHBoxLayout()
        self.btn_external = QPushButton(Translator.get("readme_open_ext"))
        self.btn_external.clicked.connect(self.open_external)
        bottom_layout.addWidget(self.btn_external)
        bottom_layout.addStretch()

        btn_close = QPushButton(Translator.get("btn_close"))
        btn_close.setObjectName("launch_installer_btn")
        btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(btn_close)

        layout.addLayout(bottom_layout)
        self.update_content()

    def get_readme_path(self, lang):
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filenames = [f'readme_{lang}.txt', 'readme_en.txt', 'readme.txt']

        for fn in filenames:
            local = os.path.join(app_dir, fn)
            if os.path.exists(local):
                return local
            system = os.path.join("/usr/share/zelix-hello", fn)
            if os.path.exists(system):
                return system
        return None

    def update_content(self):
        languages = ('en', 'tr', 'es')
        next_language = languages[(languages.index(self.current_lang) + 1) % len(languages)]
        self.btn_lang.setText({'en':'English', 'tr':'Türkçe', 'es':'Español'}[next_language])

        path = self.get_readme_path(self.current_lang)
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.text_view.setPlainText(f.read())
            except Exception as e:
                self.text_view.setPlainText(Translator.get('readme_error').format(error=e))
        else:
            self.text_view.setPlainText(Translator.get('readme_missing'))

    def toggle_language(self):
        languages = ('en', 'tr', 'es')
        self.current_lang = languages[(languages.index(self.current_lang) + 1) % len(languages)]
        self.update_content()

    def open_external(self):
        path = self.get_readme_path(self.current_lang)
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QDesktopServices.openUrl(QUrl("https://github.com/ZelixOS"))

class DashboardTab(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self._init_ui()
        Translator.add_listener(self)

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(42, 34, 42, 20)
        self.main_layout.setSpacing(12)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        self.title = QLabel()
        self.title.setObjectName("dashboard_title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("dashboard_subtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.subtitle.setWordWrap(True)
        self.subtitle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)

        self.main_layout.addLayout(header_layout)
        self.main_layout.addSpacing(12)

        self.btn_software = QPushButton()
        self.btn_system = QPushButton()
        self.btn_readme = QPushButton()
        self.btn_release_info = QPushButton()
        self.btn_wiki = QPushButton()
        self.btn_forum = QPushButton()
        self.btn_get_involved = QPushButton()
        self.btn_donate = QPushButton()

        self.lbl_start = QLabel()
        self.lbl_start.setObjectName("section_title")
        self.main_layout.addWidget(self.lbl_start)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        self.btn_software.setObjectName("dashboard_primary")
        self.btn_system.setObjectName("dashboard_action")
        self.btn_software.setMinimumHeight(58)
        self.btn_system.setMinimumHeight(58)
        actions_layout.addWidget(self.btn_software, 1)
        actions_layout.addWidget(self.btn_system, 1)
        self.main_layout.addLayout(actions_layout)
        self.main_layout.addSpacing(18)

        self.lbl_doc = QLabel()
        self.lbl_doc.setObjectName("section_title")
        self.main_layout.addWidget(self.lbl_doc)

        resources_grid = QGridLayout()
        resources_grid.setHorizontalSpacing(10)
        resources_grid.setVerticalSpacing(10)
        for button in (
            self.btn_readme, self.btn_release_info, self.btn_wiki,
            self.btn_forum, self.btn_get_involved, self.btn_donate,
        ):
            button.setObjectName("dashboard_link")
            button.setMinimumHeight(46)
        resources_grid.addWidget(self.btn_readme, 0, 0)
        resources_grid.addWidget(self.btn_release_info, 0, 1)
        resources_grid.addWidget(self.btn_wiki, 0, 2)
        resources_grid.addWidget(self.btn_forum, 1, 0)
        resources_grid.addWidget(self.btn_get_involved, 1, 1)
        resources_grid.addWidget(self.btn_donate, 1, 2)
        self.main_layout.addLayout(resources_grid)

        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(0)

        left_footer = QWidget()
        left_footer.setFixedWidth(230)
        left_footer_layout = QHBoxLayout(left_footer)
        left_footer_layout.setContentsMargins(0, 0, 0, 0)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "English")
        self.lang_combo.addItem("Türkçe", "Turkish")
        self.lang_combo.addItem("Español", "Spanish")
        idx = self.lang_combo.findData(Translator.get_language())
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.setFixedWidth(150)
        self.lang_combo.currentIndexChanged.connect(self.change_language)

        left_footer_layout.addWidget(self.lang_combo)
        left_footer_layout.addStretch()
        footer_layout.addWidget(left_footer)
        footer_layout.addStretch()

        social_layout = QHBoxLayout()
        social_layout.setSpacing(10)
        btn_yt = QPushButton()
        btn_reddit = QPushButton()
        btn_gh = QPushButton()
        btn_yt.setObjectName("social_btn")
        btn_reddit.setObjectName("social_btn")
        btn_gh.setObjectName("social_btn")
        btn_yt.setIcon(get_asset_icon("youtube.svg"))
        btn_reddit.setIcon(get_asset_icon("reddit.svg"))
        btn_gh.setIcon(get_asset_icon("github.svg"))
        btn_yt.setIconSize(QSize(20, 20))
        btn_reddit.setIconSize(QSize(20, 20))
        btn_gh.setIconSize(QSize(20, 20))
        btn_yt.setToolTip("YouTube")
        btn_reddit.setToolTip("Reddit")
        btn_reddit.setAccessibleName("Reddit")
        btn_gh.setToolTip("GitHub")
        social_layout.addWidget(btn_yt)
        social_layout.addWidget(btn_reddit)
        social_layout.addWidget(btn_gh)
        footer_layout.addLayout(social_layout)

        footer_layout.addStretch()

        right_footer = QWidget()
        right_footer.setFixedWidth(230)
        right_footer_layout = QHBoxLayout(right_footer)
        right_footer_layout.setContentsMargins(0, 0, 0, 0)
        right_footer_layout.addStretch()

        self.lbl_launch = QLabel()
        self.lbl_launch.setObjectName("footer_text")

        self.btn_autostart = QPushButton()
        self.btn_autostart.setCheckable(True)
        self.btn_autostart.setObjectName("toggle_btn")
        self.btn_autostart.clicked.connect(self.toggle_autostart)

        self.autostart_path = os.path.expanduser("~/.config/autostart/zelix-hello.desktop")
        self.system_autostart_path = "/etc/xdg/autostart/zelix-hello.desktop"

        if os.path.exists(self.autostart_path) or os.path.exists(self.system_autostart_path):
            self.btn_autostart.setChecked(True)
            self.btn_autostart.setText(Translator.get("toggle_on"))
        else:
            self.btn_autostart.setChecked(False)
            self.btn_autostart.setText(Translator.get("toggle_off"))

        right_footer_layout.addWidget(self.lbl_launch)
        right_footer_layout.addWidget(self.btn_autostart)
        footer_layout.addWidget(right_footer)

        self.main_layout.addLayout(footer_layout)

        # Connect actions
        self.btn_software.clicked.connect(lambda: self.parent_window.navigate_to(1))
        self.btn_system.clicked.connect(lambda: self.parent_window.navigate_to(2))

        # Connect URLs
        self.btn_readme.clicked.connect(self.open_readme)
        self.btn_wiki.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://docs.zelixos.com")))
        self.btn_forum.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://forum.zelixos.org")))
        self.btn_release_info.clicked.connect(self.open_release_info)
        self.btn_get_involved.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ZelixOS")))
        self.btn_donate.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://zelixos.com/")))

        btn_yt.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.youtube.com/@Zelix_OS")))
        btn_reddit.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://reddit.com/r/ZelixOS")))
        btn_gh.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ZelixOS")))

        self.retranslate_ui()

    def open_readme(self):
        dialog = ReadmeDialog(self)
        dialog.exec()

    @staticmethod
    def open_release_info():
        language = "tr" if Translator.get_language() == "Turkish" else "en"
        QDesktopServices.openUrl(QUrl(f"https://zelixos.com/blog?lang={language}"))

    def change_language(self, _index):
        Translator.set_language(self.lang_combo.currentData())

    def retranslate_ui(self):
        self.lang_combo.blockSignals(True)
        self.lang_combo.setCurrentIndex(self.lang_combo.findData(Translator.get_language()))
        self.lang_combo.blockSignals(False)
        self.title.setText(Translator.get("welcome_title"))
        self.subtitle.setText(Translator.get("welcome_subtitle"))

        self.lbl_start.setText(Translator.get("start_header"))
        self.lbl_doc.setText(Translator.get("doc_header"))

        self.btn_readme.setText(Translator.get("btn_readme"))
        self.btn_release_info.setText(Translator.get("btn_release_info"))
        self.btn_wiki.setText(Translator.get("btn_wiki"))
        self.btn_forum.setText(Translator.get("btn_forum"))
        self.btn_software.setText(Translator.get("btn_software"))
        self.btn_system.setText(Translator.get("btn_system"))
        self.btn_get_involved.setText(Translator.get("btn_get_involved"))
        self.btn_donate.setText(Translator.get("btn_donate"))

        self.lbl_launch.setText(Translator.get("lbl_launch_start"))
        if self.btn_autostart.isChecked():
            self.btn_autostart.setText(Translator.get("toggle_on"))
        else:
            self.btn_autostart.setText(Translator.get("toggle_off"))

    def toggle_autostart(self):
        autostart_dir = os.path.expanduser("~/.config/autostart")
        if not os.path.exists(autostart_dir):
            os.makedirs(autostart_dir, exist_ok=True)

        if self.btn_autostart.isChecked():
            self.btn_autostart.setText(Translator.get("toggle_on"))
            desktop_content = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=Zelix Hello\n"
                "Comment=Welcome to ZelixOS\n"
                "Exec=zelix-hello\n"
                "Icon=zelixos\n"
                "Terminal=false\n"
            )
            try:
                orig_file = "/usr/share/applications/zelix-hello.desktop"
                if os.path.exists(self.autostart_path) or os.path.islink(self.autostart_path):
                    os.remove(self.autostart_path)
                if os.path.exists(orig_file):
                    os.symlink(orig_file, self.autostart_path)
                else:
                    with open(self.autostart_path, "w", encoding="utf-8") as f:
                        f.write(desktop_content)
            except Exception as e:
                print(f"Error enabling autostart: {e}")
        else:
            self.btn_autostart.setText(Translator.get("toggle_off"))
            # Remove user autostart
            if os.path.exists(self.autostart_path) or os.path.islink(self.autostart_path):
                try:
                    os.remove(self.autostart_path)
                except Exception as e:
                    print(f"Error disabling user autostart: {e}")

            # Remove system autostart
            if os.path.exists(self.system_autostart_path):
                try:
                    subprocess.run(["pkexec", "rm", "-f", self.system_autostart_path], check=False)
                except Exception as e:
                    print(f"Error disabling system autostart: {e}")
