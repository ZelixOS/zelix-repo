import sys
import math
from language_support import LanguagePreference, LANGUAGE_NAMES, apply_qt_language
from PyQt6.QtCore import Qt, QPoint, QRect, QLineF
from PyQt6.QtGui import QPainter, QPen, QColor, QPolygonF, QGuiApplication, QImage, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, 
    QColorDialog, QSlider, QLabel, QFrame, QFileDialog, QMessageBox, QComboBox
)

TRANSLATIONS = {'en': {'pointer': 'Pointer',
        'pen': 'Pen',
        'line': 'Line',
        'arrow': 'Arrow',
        'rect': 'Rectangle',
        'circle': 'Circle',
        'eraser': 'Eraser',
        'pointer_tip': 'Use applications underneath; select a drawing tool to resume.',
        'color': 'Choose color',
        'width': 'Width:',
        'undo': 'Undo (Ctrl+Z)',
        'redo': 'Redo (Ctrl+Shift+Z)',
        'save_tip': 'Save the drawing as a transparent PNG',
        'clear': 'Clear screen',
        'close': 'Exit (Esc)',
        'clear_confirm': 'Clear all drawings?',
        'save': 'Save drawing',
        'save_error_title': 'Save error',
        'save_error': 'The drawing could not be saved.',
        'language': 'Language'},
 'tr': {'pointer': 'İmleç',
        'pen': 'Kalem',
        'line': 'Çizgi',
        'arrow': 'Ok',
        'rect': 'Kutu',
        'circle': 'Daire',
        'eraser': 'Silgi',
        'pointer_tip': 'Alttaki uygulamaları kullan; çizime dönmek için bir araç seç.',
        'color': 'Renk seç',
        'width': 'Kalınlık:',
        'undo': 'Geri al (Ctrl+Z)',
        'redo': 'Yinele (Ctrl+Shift+Z)',
        'save_tip': 'Çizimi şeffaf PNG olarak kaydet',
        'clear': 'Ekranı temizle',
        'close': 'Çıkış (Esc)',
        'clear_confirm': 'Tüm çizimler temizlensin mi?',
        'save': 'Çizimi kaydet',
        'save_error_title': 'Kaydetme hatası',
        'save_error': 'Çizim kaydedilemedi.',
        'language': 'Dil'},
 'es': {'pointer': 'Puntero',
        'pen': 'Lápiz',
        'line': 'Línea',
        'arrow': 'Flecha',
        'rect': 'Rectángulo',
        'circle': 'Círculo',
        'eraser': 'Borrador',
        'pointer_tip': 'Usa las aplicaciones debajo; elige una herramienta para volver a dibujar.',
        'color': 'Elegir color',
        'width': 'Grosor:',
        'undo': 'Deshacer (Ctrl+Z)',
        'redo': 'Rehacer (Ctrl+Mayús+Z)',
        'save_tip': 'Guardar el dibujo como PNG transparente',
        'clear': 'Limpiar pantalla',
        'close': 'Salir (Esc)',
        'clear_confirm': '¿Borrar todos los dibujos?',
        'save': 'Guardar dibujo',
        'save_error_title': 'Error al guardar',
        'save_error': 'No se pudo guardar el dibujo.',
        'language': 'Idioma'}}

class FloatingToolbar(QFrame):
    """Ekran üzerinde sürüklenebilir yüzen menü"""
    def __init__(self, canvas, floating=False):
        if floating:
            super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        else:
            super().__init__(canvas)
        self.canvas = canvas
        self.drag_position = QPoint()

        # KDE Breeze Dark uyumlu modern stil
        self.setStyleSheet("""
            FloatingToolbar {
                background-color: rgba(30, 31, 41, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
            }
            QPushButton {
                background-color: #31363b;
                color: #eff0f1;
                border: 1px solid #4d4d4d;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3daee9;
                color: #ffffff;
            }
            QPushButton:checked {
                background-color: #3daee9;
                color: #ffffff;
            }
            QLabel {
                color: #eff0f1;
                font-size: 11px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(5)

        # Sürükleme Tutamağı
        self.drag_handle = QLabel("⣿", self)
        self.drag_handle.setStyleSheet("font-size: 16px; color: #7f8c8d; cursor: move;")
        layout.addWidget(self.drag_handle)

        self.btn_pointer = QPushButton("↖ İmleç", self)
        self.btn_pointer.setCheckable(True)
        self.btn_pointer.setToolTip("Alttaki uygulamaları kullan; çizime dönmek için bir araç seç")
        self.btn_pointer.clicked.connect(lambda: self.set_mode("pointer"))
        layout.addWidget(self.btn_pointer)

        # Araç Butonları
        self.btn_pen = QPushButton("✏️ Kalem", self)
        self.btn_pen.setCheckable(True)
        self.btn_pen.setChecked(True)
        self.btn_pen.clicked.connect(lambda: self.set_mode("pen"))
        layout.addWidget(self.btn_pen)

        self.btn_line = QPushButton("📏 Çizgi", self)
        self.btn_line.setCheckable(True)
        self.btn_line.clicked.connect(lambda: self.set_mode("line"))
        layout.addWidget(self.btn_line)

        self.btn_arrow = QPushButton("➡️ Ok", self)
        self.btn_arrow.setCheckable(True)
        self.btn_arrow.clicked.connect(lambda: self.set_mode("arrow"))
        layout.addWidget(self.btn_arrow)

        self.btn_rect = QPushButton("🔲 Kutu", self)
        self.btn_rect.setCheckable(True)
        self.btn_rect.clicked.connect(lambda: self.set_mode("rect"))
        layout.addWidget(self.btn_rect)

        self.btn_circle = QPushButton("⭕ Daire", self)
        self.btn_circle.setCheckable(True)
        self.btn_circle.clicked.connect(lambda: self.set_mode("circle"))
        layout.addWidget(self.btn_circle)

        self.btn_eraser = QPushButton("🧹 Silgi", self)
        self.btn_eraser.setCheckable(True)
        self.btn_eraser.clicked.connect(lambda: self.set_mode("eraser"))
        layout.addWidget(self.btn_eraser)

        # Renk ve Kalınlık
        self.btn_color = QPushButton("🎨", self)
        self.btn_color.setToolTip("Renk Seç")
        self.btn_color.clicked.connect(self.choose_color)
        layout.addWidget(self.btn_color)

        self.width_label = QLabel()
        layout.addWidget(self.width_label)
        self.slider_width = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_width.setRange(2, 30)
        self.slider_width.setValue(4)
        self.slider_width.setFixedWidth(65)
        self.slider_width.valueChanged.connect(self.change_width)
        layout.addWidget(self.slider_width)

        # Aksiyonlar
        self.btn_undo = QPushButton("↩️", self)
        self.btn_undo.setToolTip("Geri Al (Ctrl+Z)")
        self.btn_undo.clicked.connect(self.canvas.undo)
        layout.addWidget(self.btn_undo)

        self.btn_redo = QPushButton("↪️", self)
        self.btn_redo.setToolTip("Yinele (Ctrl+Shift+Z)")
        self.btn_redo.clicked.connect(self.canvas.redo)
        layout.addWidget(self.btn_redo)

        self.btn_save = QPushButton("💾", self)
        self.btn_save.setToolTip("Çizimi şeffaf PNG olarak kaydet")
        self.btn_save.clicked.connect(self.canvas.save_canvas)
        layout.addWidget(self.btn_save)

        self.btn_clear = QPushButton("🗑️", self)
        self.btn_clear.setToolTip("Ekranı Temizle")
        self.btn_clear.clicked.connect(self.canvas.clear_canvas)
        layout.addWidget(self.btn_clear)

        self.btn_close = QPushButton("❌", self)
        self.btn_close.setToolTip("Çıkış (Esc)")
        self.btn_close.clicked.connect(self.canvas.close_application)
        layout.addWidget(self.btn_close)

        self.language_combo = QComboBox()
        for code, name in LANGUAGE_NAMES.items():
            self.language_combo.addItem(code.upper(), code)
            self.language_combo.setItemData(self.language_combo.count()-1, name, Qt.ItemDataRole.ToolTipRole)
        self.language_combo.setFixedWidth(62)
        self.language_combo.setCurrentIndex(self.language_combo.findData(self.canvas.language_preference.language))
        self.language_combo.currentIndexChanged.connect(lambda: self.canvas.set_language(self.language_combo.currentData()))
        layout.addWidget(self.language_combo)

        self.tool_buttons = [
            self.btn_pointer, self.btn_pen, self.btn_line, self.btn_arrow, 
            self.btn_rect, self.btn_circle, self.btn_eraser
        ]

        self.retranslate_ui()

    def retranslate_ui(self):
        symbols = {'pointer':'↖', 'pen':'✏️', 'line':'📏', 'arrow':'➡️', 'rect':'🔲', 'circle':'⭕', 'eraser':'🧹'}
        for name, symbol in symbols.items():
            getattr(self, 'btn_' + name).setText(symbol + ' ' + self.canvas.t(name))
        self.btn_pointer.setToolTip(self.canvas.t('pointer_tip'))
        self.btn_color.setToolTip(self.canvas.t('color'))
        self.width_label.setText(self.canvas.t('width'))
        for name, key in (('undo','undo'),('redo','redo'),('save','save_tip'),('clear','clear'),('close','close')):
            getattr(self, 'btn_' + name).setToolTip(self.canvas.t(key))
        self.language_combo.blockSignals(True)
        self.language_combo.setCurrentIndex(self.language_combo.findData(self.canvas.language_preference.language))
        self.language_combo.blockSignals(False)
        self.language_combo.setToolTip(self.canvas.t('language'))
        self.language_combo.setAccessibleName(self.canvas.t('language'))

    def set_mode(self, mode):
        self.canvas.set_pointer_mode(mode == "pointer")
        if mode != "pointer":
            self.canvas.current_mode = mode
        for toolbar in (self.canvas.toolbar, self.canvas.pointer_toolbar):
            for btn in toolbar.tool_buttons:
                btn.setChecked(False)
        
        target = self.canvas.pointer_toolbar if mode == "pointer" else self.canvas.toolbar
        if mode == "pointer": target.btn_pointer.setChecked(True)
        elif mode == "pen": target.btn_pen.setChecked(True)
        elif mode == "line": target.btn_line.setChecked(True)
        elif mode == "arrow": target.btn_arrow.setChecked(True)
        elif mode == "rect": target.btn_rect.setChecked(True)
        elif mode == "circle": target.btn_circle.setChecked(True)
        elif mode == "eraser": target.btn_eraser.setChecked(True)

    def choose_color(self):
        color = QColorDialog.getColor(self.canvas.current_color, self, self.canvas.t("color"))
        if color.isValid():
            self.canvas.current_color = color

    def change_width(self, val):
        self.canvas.pen_width = val

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.mapToGlobal(QPoint(0, 0))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            position = event.globalPosition().toPoint() - self.drag_position
            self.move(self.parentWidget().mapFromGlobal(position) if self.parentWidget() else position)
            event.accept()


class Canvas(QWidget):
    """KDE Plasma Wayland Uyumlu Tam Ekran Katmanı"""
    def __init__(self):
        super().__init__()
        self.language_preference = LanguagePreference('pen')
        apply_qt_language(self.language_preference.language)

        # Plasma Wayland için kritik pencere bayrakları
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # Tüm bağlı ekran alanını otomatik kapla
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

        # Çizim değişkenleri
        self.drawing = False
        self.start_point = QPoint()
        self.current_point = QPoint()
        
        self.shapes = []
        self.redo_stack = []
        self.pointer_mode = False
        self.current_mode = "pen"
        self.current_color = QColor(235, 77, 75)
        self.pen_width = 4
        self.current_freehand_points = []

        # Çizim sırasında çubuk katmanın içindedir; imleç modunda ayrı pencere kullanılır.
        self.toolbar = FloatingToolbar(self)
        self.pointer_toolbar = FloatingToolbar(self, floating=True)
        self.toolbar.adjustSize()
        self.pointer_toolbar.adjustSize()
        self.toolbar.move(40, 40)
        self.pointer_toolbar.move(screen_geometry.topLeft() + QPoint(40, 40))
        for toolbar in (self.toolbar, self.pointer_toolbar):
            for sequence, action in (("Ctrl+Z", self.undo), ("Ctrl+Shift+Z", self.redo), ("Esc", self.close_application)):
                shortcut = QShortcut(QKeySequence(sequence), toolbar)
                shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
                shortcut.activated.connect(action)
        self.show()
        self.toolbar.show()

    def t(self, key):
        return TRANSLATIONS[self.language_preference.language].get(key, TRANSLATIONS['en'].get(key, key))

    def set_language(self, code):
        self.language_preference.set_language(code)
        apply_qt_language(code)
        for toolbar in (self.toolbar, self.pointer_toolbar):
            toolbar.retranslate_ui()
            toolbar.adjustSize()

    def set_pointer_mode(self, enabled):
        if self.pointer_mode == enabled:
            return
        self.pointer_mode = enabled
        self.drawing = False
        self.current_freehand_points = []
        if enabled:
            self.pointer_toolbar.move(self.toolbar.mapToGlobal(QPoint(0, 0)))
            self.pointer_toolbar.show()
            self.pointer_toolbar.raise_()
            self.hide()
        else:
            position = self.pointer_toolbar.pos() - self.geometry().topLeft()
            self.toolbar.move(position)
            self.show()
            self.toolbar.show()
            self.pointer_toolbar.hide()
        self.update()

    def close_application(self):
        self.pointer_toolbar.close()
        self.toolbar.close()
        self.close()
        QApplication.instance().quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.start_point = event.position().toPoint()
            self.current_point = self.start_point
            
            if self.current_mode in ["pen", "eraser"]:
                self.current_freehand_points = [self.start_point]

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            self.current_point = event.position().toPoint()
            if self.current_mode in ["pen", "eraser"]:
                self.current_freehand_points.append(self.current_point)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.drawing = False
            self.current_point = event.position().toPoint()

            shape_data = {
                "type": self.current_mode,
                "color": QColor(self.current_color),
                "width": self.pen_width,
                "start": self.start_point,
                "end": self.current_point,
                "points": list(self.current_freehand_points)
            }
            self.shapes.append(shape_data)
            self.redo_stack.clear()
            self.current_freehand_points = []
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Eski Çizimler
        for shape in self.shapes:
            self.draw_shape(painter, shape)

        # 2. Önizleme Çizimi
        if self.drawing:
            temp_shape = {
                "type": self.current_mode,
                "color": QColor(self.current_color),
                "width": self.pen_width,
                "start": self.start_point,
                "end": self.current_point,
                "points": self.current_freehand_points
            }
            self.draw_shape(painter, temp_shape)

    def draw_shape(self, painter, shape):
        stype = shape["type"]
        width = shape["width"]
        color = shape["color"]

        if stype == "eraser":
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            pen = QPen(QColor(0, 0, 0, 255), width * 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        else:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        start = shape["start"]
        end = shape["end"]

        if stype in ["pen", "eraser"]:
            pts = shape["points"]
            if len(pts) == 1:
                painter.drawPoint(pts[0])
            for i in range(len(pts) - 1):
                painter.drawLine(pts[i], pts[i + 1])
        elif stype == "line":
            painter.drawLine(start, end)
        elif stype == "rect":
            rect = QRect(start, end).normalized()
            painter.drawRect(rect)
        elif stype == "circle":
            rect = QRect(start, end).normalized()
            painter.drawEllipse(rect)
        elif stype == "arrow":
            self.draw_arrow(painter, start, end, width)

    def draw_arrow(self, painter, start, end, width):
        painter.drawLine(start, end)
        line = QLineF(start, end)
        if line.length() < 5:
            return
        
        angle = math.atan2(-line.dy(), line.dx())
        arrow_size = 15 + width
        
        p1 = end - QPoint(int(math.cos(angle + math.pi / 6) * arrow_size),
                          int(-math.sin(angle + math.pi / 6) * arrow_size))
        p2 = end - QPoint(int(math.cos(angle - math.pi / 6) * arrow_size),
                          int(-math.sin(angle - math.pi / 6) * arrow_size))

        arrow_head = QPolygonF([end, p1, p2])
        painter.setBrush(painter.pen().color())
        painter.drawPolygon(arrow_head)

    def undo(self):
        if self.shapes:
            self.redo_stack.append(self.shapes.pop())
            self.update()

    def redo(self):
        if self.redo_stack:
            self.shapes.append(self.redo_stack.pop())
            self.update()

    def clear_canvas(self):
        if not self.shapes:
            return
        answer = QMessageBox.question(self.pointer_toolbar if self.pointer_mode else self.toolbar, self.t("clear"), self.t("clear_confirm"))
        if answer == QMessageBox.StandardButton.Yes:
            self.shapes.clear()
            self.redo_stack.clear()
            self.update()

    def save_canvas(self):
        path, _ = QFileDialog.getSaveFileName(self.pointer_toolbar if self.pointer_mode else self.toolbar, self.t("save"), "zelixpen.png", "PNG (*.png)")
        if not path:
            return
        if not path.lower().endswith(".png"):
            path += ".png"
        image = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for shape in self.shapes:
            self.draw_shape(painter, shape)
        painter.end()
        if not image.save(path, "PNG"):
            QMessageBox.warning(self.pointer_toolbar if self.pointer_mode else self.toolbar, self.t("save_error_title"), self.t("save_error"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setDesktopFileName("zelixpen")
    canvas = Canvas()
    sys.exit(app.exec())
