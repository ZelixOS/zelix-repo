import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.language_support import apply_qt_language
from utils.translations import Translator

def main():
    app = QApplication(sys.argv)
    apply_qt_language(Translator._preference.language)

    # Load stylesheet — gracefully handle missing or inaccessible files
    style_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    try:
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
    except (OSError, PermissionError) as e:
        print(f"[Warning] Could not load stylesheet: {e}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
