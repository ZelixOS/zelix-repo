import os
import sys
from language_support import LanguagePreference, LANGUAGE_NAMES, apply_qt_language

from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QCloseEvent, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget,
)


TRANSLATIONS = {'en': {'idle': 'Check for updates',
        'detail': 'Official and configured pacman repositories are checked. AUR packages are not included.',
        'check': 'Check for updates',
        'update': 'Update system',
        'checking': 'Checking for updates…',
        'confirm_title': 'Confirm update',
        'confirm_text': 'System packages will be updated. Administrator privileges are required and pacman '
                        'prompts use their default answers. Continue?',
        'updating': 'Updating the system…',
        'failed_start': 'The process could not start.',
        'missing_checktools': 'Update check could not start. Ensure pacman-contrib and fakeroot are '
                              'installed: sudo pacman -Syu pacman-contrib fakeroot',
        'available': '{count} packages can be updated.',
        'no_updates': 'The system appears up to date.',
        'check_failed': 'Could not check for updates.',
        'error_code': 'Error code: {code}',
        'done': 'Update complete.',
        'restart': 'You may need to restart the system for some updates to take effect.',
        'auth_denied': 'Authorization was cancelled or denied.',
        'failed': 'Update failed (code: {code}).',
        'still_running_title': 'Operation in progress',
        'still_running_text': 'Wait for the operation to finish before closing the window.',
        'language': 'Language'},
 'tr': {'idle': 'Güncellemeleri kontrol edin',
        'detail': 'Resmî depolar ve yapılandırılmış pacman depoları kontrol edilir. AUR paketleri dahil '
                  'değildir.',
        'check': 'Güncellemeleri kontrol et',
        'update': 'Sistemi güncelle',
        'checking': 'Güncellemeler kontrol ediliyor…',
        'confirm_title': 'Güncellemeyi onayla',
        'confirm_text': 'Sistem paketleri güncellenecek. İşlem yönetici yetkisi gerektirir ve pacman '
                        'sorularında varsayılan yanıtlar kullanılır. Devam edilsin mi?',
        'updating': 'Sistem güncelleniyor…',
        'failed_start': 'İşlem başlatılamadı.',
        'missing_checktools': 'Güncelleme kontrolü başlatılamadı. pacman-contrib ve fakeroot paketlerini '
                              'denetleyin: sudo pacman -Syu pacman-contrib fakeroot',
        'available': '{count} paket güncellenebilir.',
        'no_updates': 'Sistem güncel görünüyor.',
        'check_failed': 'Güncellemeler kontrol edilemedi.',
        'error_code': 'Hata kodu: {code}',
        'done': 'Güncelleme tamamlandı.',
        'restart': 'Bazı güncellemelerin etkinleşmesi için sistemi yeniden başlatmanız gerekebilir.',
        'auth_denied': 'Yetkilendirme iptal edildi veya reddedildi.',
        'failed': 'Güncelleme başarısız oldu (kod: {code}).',
        'still_running_title': 'İşlem sürüyor',
        'still_running_text': 'Pencereyi kapatmadan önce işlemin tamamlanmasını bekleyin.',
        'language': 'Dil'},
 'es': {'idle': 'Buscar actualizaciones',
        'detail': 'Se consultan los repositorios oficiales y configurados en pacman. No se incluyen paquetes '
                  'del AUR.',
        'check': 'Buscar actualizaciones',
        'update': 'Actualizar sistema',
        'checking': 'Buscando actualizaciones…',
        'confirm_title': 'Confirmar actualización',
        'confirm_text': 'Se actualizarán los paquetes del sistema. Se necesitan permisos de administrador y '
                        'las preguntas de pacman usarán las respuestas predeterminadas. ¿Quieres continuar?',
        'updating': 'Actualizando el sistema…',
        'failed_start': 'No se pudo iniciar el proceso.',
        'missing_checktools': 'No se pudo iniciar la búsqueda. Comprueba que pacman-contrib y fakeroot estén '
                              'instalados: sudo pacman -Syu pacman-contrib fakeroot',
        'available': 'Hay {count} paquetes disponibles para actualizar.',
        'no_updates': 'El sistema está actualizado.',
        'check_failed': 'No se pudieron buscar actualizaciones.',
        'error_code': 'Código de error: {code}',
        'done': 'Actualización completada.',
        'restart': 'Puede ser necesario reiniciar el sistema para aplicar algunas actualizaciones.',
        'auth_denied': 'La autorización se canceló o se denegó.',
        'failed': 'La actualización falló (código: {code}).',
        'still_running_title': 'Operación en curso',
        'still_running_text': 'Espera a que termine la operación antes de cerrar la ventana.',
        'language': 'Idioma'}}


class UpdaterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language_preference = LanguagePreference('updater')
        apply_qt_language(self.language_preference.language)
        self._status_key, self._status_values = 'idle', {}
        self.setWindowTitle("ZelixOS Updater")
        for path in ("/usr/share/zelix/zelix-updater.png", "/usr/share/pixmaps/zelix-updater.png"):
            if os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                break
        self.resize(760, 560)
        self.setStyleSheet("""
            QMainWindow { background: #0e0f12; }
            QLabel { color: white; font-family: 'Noto Sans', sans-serif; }
            QPushButton { background: white; color: black; font-weight: bold;
                border: 1px solid white; border-radius: 6px; padding: 10px; }
            QPushButton:hover { background: #e0e0e0; }
            QPushButton:disabled { background: #18191e; color: #777780; border-color: #24252c; }
            QProgressBar { border: 1px solid #282932; border-radius: 6px;
                background: #16171b; color: white; text-align: center; }
            QProgressBar::chunk { background: white; border-radius: 4px; }
            QTextEdit { background: #0a0b0e; color: #d8d8e0; border: 1px solid #202126;
                border-radius: 6px; padding: 8px; }
        """)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        language_row = QHBoxLayout()
        language_row.addStretch()
        self.language_combo = QComboBox()
        for code, name in LANGUAGE_NAMES.items():
            self.language_combo.addItem(name, code)
        self.language_combo.setCurrentIndex(self.language_combo.findData(self.language_preference.language))
        language_row.addWidget(self.language_combo)
        layout.addLayout(language_row)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.status_label)
        self.detail_label = QLabel()
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Monospace", 10))
        layout.addWidget(self.log_view)
        buttons = QHBoxLayout()
        self.check_button = QPushButton()
        self.check_button.clicked.connect(self.check_updates)
        self.update_button = QPushButton()
        self.update_button.setEnabled(False)
        self.update_button.clicked.connect(self.start_update)
        buttons.addWidget(self.check_button)
        buttons.addWidget(self.update_button)
        layout.addLayout(buttons)
        self.process = None
        self.operation = None
        self.stdout = bytearray()
        self.stderr = bytearray()
        self.packages = []
        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.retranslate_ui()

    def t(self, key, **values):
        return TRANSLATIONS[self.language_preference.language].get(key, TRANSLATIONS['en'].get(key, key)).format(**values)

    def set_status(self, key, **values):
        self._status_key, self._status_values = key, values
        self.status_label.setText(self.t(key, **values))

    def change_language(self, *_args):
        self.language_preference.set_language(self.language_combo.currentData())
        apply_qt_language(self.language_preference.language)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.language_combo.setAccessibleName(self.t('language'))
        self.language_combo.setToolTip(self.t('language'))
        self.detail_label.setText(self.t('detail'))
        self.check_button.setText(self.t('check'))
        self.update_button.setText(self.t('update'))
        self.status_label.setText(self.t(self._status_key, **self._status_values))

    def set_busy(self, busy):
        self.check_button.setEnabled(not busy)
        self.update_button.setEnabled(not busy and bool(self.packages))
        self.progress_bar.setRange(0, 0 if busy else 1)
        if not busy:
            self.progress_bar.setValue(0)

    def run_process(self, operation, program, args):
        self.operation = operation
        self.stdout = bytearray()
        self.stderr = bytearray()
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)
        self.set_busy(True)
        self.process.start(program, args)

    def check_updates(self):
        self.packages = []
        self.log_view.clear()
        self.set_status('checking')
        self.run_process("check", "checkupdates", [])

    def start_update(self):
        answer = QMessageBox.question(
            self, self.t('confirm_title'), self.t('confirm_text'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.log_view.clear()
        self.set_status('updating')
        self.run_process("update", "pkexec", ["pacman", "-Syu", "--noconfirm"])

    def read_stdout(self):
        data = bytes(self.process.readAllStandardOutput())
        self.stdout.extend(data)
        if self.operation == "update":
            self.append_output(data)

    def read_stderr(self):
        data = bytes(self.process.readAllStandardError())
        self.stderr.extend(data)
        if self.operation == "update":
            self.append_output(data)

    def append_output(self, data):
        cursor = self.log_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(data.decode("utf-8", errors="replace").replace("\r", "\n"))
        self.log_view.setTextCursor(cursor)
        self.log_view.ensureCursorVisible()

    def process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.set_status('failed_start')
            if self.operation == "check":
                self.log_view.append(self.t('missing_checktools'))
            else:
                self.log_view.append(self.process.errorString())
            self.operation = None
            self.set_busy(False)

    def process_finished(self, code, exit_status):
        self.read_stdout()
        self.read_stderr()
        operation = self.operation
        self.operation = None
        success = exit_status == QProcess.ExitStatus.NormalExit
        if operation == "check":
            output = self.stdout.decode("utf-8", errors="replace").strip()
            error = self.stderr.decode("utf-8", errors="replace").strip()
            if success and code == 0 and output:
                self.packages = output.splitlines()
                self.log_view.setPlainText(output)
                self.set_status('available', count=len(self.packages))
                if error:
                    self.log_view.append("\n" + error)
            elif success and code == 2:
                self.set_status('no_updates')
                if error:
                    self.log_view.setPlainText(error)
            else:
                self.set_status('check_failed')
                self.log_view.setPlainText("\n".join(part for part in (output, error) if part) or self.t('error_code', code=code))
        elif operation == "update":
            self.packages = []
            if success and code == 0:
                self.set_status('done')
                self.log_view.append('\n' + self.t('restart'))
            elif success and code in (126, 127):
                self.set_status('auth_denied')
            else:
                self.set_status('failed', code=code)
        self.set_busy(False)
        self.process.deleteLater()
        self.process = None

    def closeEvent(self, event: QCloseEvent):
        if self.operation:
            QMessageBox.information(self, self.t('still_running_title'), self.t('still_running_text'))
            event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setDesktopFileName("zelix-updater")
    window = UpdaterWindow()
    window.show()
    sys.exit(app.exec())
