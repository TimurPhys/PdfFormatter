import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QLineEdit,
    QMessageBox,
    QProgressBar,
)
from PyQt5.QtCore import Qt
from worker import PDFWorker
from settings.settings_manager import SettingsManager
from protection import check_protection


### ГЛАВНОЕ ОКНО
class PDFProcessorGUI(QWidget):
    def __init__(self):
        super().__init__()  # Вызываем конструктор дочернего класса
        self.setWindowTitle("PDF Processor")  # Даем название окну
        self.settings_manager = SettingsManager()  # Копируем настройки в класс
        self.settings = self.settings_manager.load_settings()
        self.init_ui()  # Создаем графический интерфейс

    def init_ui(self):
        layout = QVBoxLayout()  # Фундамент интерфейса

        # --- Выбор файла ---
        file_layout = (
            QHBoxLayout()
        )  # Горизонатльный layout, размещает элементы слева направо
        self.file_label_pdf = QLabel("Выберите PDF файл:")  # Тупо текст
        self.file_path_pdf = QLineEdit()  # Однострочный ввод
        self.browse_btn_pdf = QPushButton("Обзор")  # Кнопка "Обзор"
        self.browse_btn_pdf.clicked.connect(
            lambda: self.browse_file("pdf")
        )  # Привязываем нажатие кнопки к выполнению функции

        self.file_label_html = QLabel(
            "Выберите <a href='https://tools.pdf24.org/en/pdf-to-html'>HTML файл</a>:"
        )  # Тупо текст
        self.file_label_html.setOpenExternalLinks(True)
        self.file_label_html.setCursor(Qt.CursorShape.PointingHandCursor)

        self.file_path_html = QLineEdit()  # Однострочный ввод
        self.browse_btn_html = QPushButton("Обзор")  # Кнопка "Обзор"
        self.browse_btn_html.clicked.connect(
            lambda: self.browse_file("html")
        )  # Привязываем нажатие кнопки к выполнению функции
        file_layout.addWidget(self.file_label_pdf)
        file_layout.addWidget(self.file_path_pdf)
        file_layout.addWidget(self.browse_btn_pdf)

        file_layout.addWidget(self.file_label_html)
        file_layout.addWidget(self.file_path_html)
        file_layout.addWidget(self.browse_btn_html)

        # --- Выбор пути сохранения ---
        save_layout = QHBoxLayout()
        self.save_label = QLabel("Выберите путь сохранения PDF файла:")  # Тупо текст
        self.save_path = QLineEdit()  # Однострочный ввод
        self.save_path_btn = QPushButton("Обзор")  # Кнопка "Обзор"
        self.save_path_btn.clicked.connect(self.browse_save_path)
        save_layout.addWidget(self.save_label)
        save_layout.addWidget(self.save_path)
        save_layout.addWidget(self.save_path_btn)

        # --- Текст, который не масштабировать ---
        self.exclude_label = QLabel(
            "Текст, который НЕ масштабировать <b>(с новой строки)</b>: "
        )  # Тупо текст
        self.exclude_text = QTextEdit()  # Поле для многострочного ввода

        # --- Кнопки ---
        btn_layout = QHBoxLayout()  # Горизонтальный layout
        self.process_btn = QPushButton("Обработать")
        self.process_btn.clicked.connect(self.process_file)
        self.admin_btn = QPushButton("⚙ Настройки")
        self.admin_btn.clicked.connect(self.admin_settings_window)
        btn_layout.addWidget(self.process_btn)
        btn_layout.addWidget(self.admin_btn)

        # --- Прогресс ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)

        # --- Статус ---
        self.status_label = QLabel("Выберите файл")

        # --- Сборка ---
        layout.addLayout(file_layout)
        layout.addLayout(save_layout)
        layout.addWidget(self.exclude_label)
        layout.addWidget(self.exclude_text)
        layout.addLayout(btn_layout)
        layout.addWidget(self.progress)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def browse_file(self, type):
        try:
            fname, _ = QFileDialog.getOpenFileName(
                self, f"Выберите {type} файл", "", f"{type} Files (*.{type})"
            )
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", e)
            return

        if fname:
            if type == "pdf":
                self.file_path_pdf.setText(fname)
            elif type == "html":
                self.file_path_html.setText(fname)
            self.status_label.setText("Файл выбран!")
            self.status_label.setStyleSheet("color: green;")
            self.progress.setVisible(False)

    def browse_save_path(self):
        try:
            fname = QFileDialog.getExistingDirectory(self, "Сохранить результат", "")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", e)
            return

        if fname:
            self.save_path.setText(fname)
            self.status_label.setText("Путь сохранения результата выбран!")
            self.status_label.setStyleSheet("color: green;")
            self.progress.setVisible(False)

    def process_file(self):
        pdf_path = self.file_path_pdf.text()
        html_path = self.file_path_html.text()
        output_path = self.save_path.text()
        self.settings["EXCEPTIONS"] = self.exclude_text.toPlainText().splitlines()

        if not pdf_path:
            QMessageBox.warning(self, "Ошибка", "Выберите PDF файл!")
            return
        if not html_path:
            QMessageBox.warning(self, "Ошибка", "Выберите HTML файл!")
            return
        if not output_path:
            QMessageBox.warning(self, "Ошибка", "Выберите путь сохранения результата!")
            return

        self.status_label.setText("Обработка...")

        self.worker = PDFWorker(pdf_path, html_path, output_path, self.settings)

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    # При окончании
    def on_finished(self):
        self.progress.setValue(100)
        self.status_label.setText("Готово! Результат: result.pdf")

    # При ошибке
    def on_error(self, msg):
        QMessageBox.critical(self, "Ошибка", msg)
        self.status_label.setText("Произошла ошибка!")
        self.status_label.setStyleSheet("color: red")
        self.progress.setVisible(False)

    def choose_dir(self, key, edits):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if directory:
            edits[key].setText(directory)
            self.settings["ICONS_DIR"] = directory

    def admin_settings_window(self):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox

        dlg = QDialog(self)
        dlg.setWindowTitle("Глубокие настройки")
        layout = QFormLayout(dlg)

        # Поля настроек
        edits = {}
        for key, val in self.settings.items():
            edits[key] = QLineEdit(str(val))
            if key == "ICONS_DIR":
                # 1. Создаем контейнер и горизонтальный слой
                h_layout = QHBoxLayout()

                # 2. Создаем кнопку "Обзор"
                btn_browse = QPushButton("Обзор")

                # 3. Добавляем поле и кнопку в этот слой
                h_layout.addWidget(edits[key])
                h_layout.addWidget(btn_browse)

                # 4. Подключаем функцию выбора папки (лямбда-функция для удобства)
                btn_browse.clicked.connect(lambda ch, k=key: self.choose_dir(k, edits))

                # 5. Добавляем в основной layout не виджет, а этот слой
                layout.addRow("ICONS_DIR:", h_layout)
            elif key == "EXCEPTIONS":
                continue
            elif key == "TARGET_W" or key == "TARGET_H":
                layout.addRow(f"{key} (мм)", edits[key])
            else:
                layout.addRow(key, edits[key])

        # Кнопки Сохранить/Отмена
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        float_keys = [
            "TARGET_W",
            "TARGET_H",
            "FACTOR",
        ]

        if dlg.exec_() == QDialog.Accepted:
            try:
                self.settings_manager.save_settings(self.settings)
                for key in edits:
                    if key in float_keys:
                        self.settings[key] = float(edits[key].text())
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"{e}")


def main():
    app = QApplication(sys.argv)
    if not check_protection():
        sys.exit(1)

    window = PDFProcessorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
