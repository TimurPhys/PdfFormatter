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
    QInputDialog,
    QProgressBar,
    QComboBox,
    QCheckBox,
)
from worker import PDFWorker
from processor import process_pdf
from config import DEFAULT_SETTINGS
import fitz
import copy


### ГЛАВНОЕ ОКНО
class PDFProcessorGUI(QWidget):
    def __init__(self):
        super().__init__()  # Вызываем конструктор дочернего класса
        self.setWindowTitle("PDF Processor")  # Даем название окну
        self.settings = copy.deepcopy(DEFAULT_SETTINGS)  # Копируем настройки в класс
        self.init_ui()  # Создаем графический интерфейс

    def init_ui(self):
        layout = QVBoxLayout()  # Фундамент интерфейса

        # --- Выбор файла ---
        file_layout = (
            QHBoxLayout()
        )  # Горизонатльный layout, размещает элементы слева направо
        self.file_label = QLabel("Выберите PDF файл:")  # Тупо текст
        self.file_path = QLineEdit()  # Однострочный ввод
        self.browse_btn = QPushButton("Обзор")  # Кнопка "Обзор"
        self.browse_btn.clicked.connect(
            self.browse_file
        )  # Привязываем нажатие кнопки к выполнению функции
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.browse_btn)

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

    def browse_file(self):
        try:
            fname, _ = QFileDialog.getOpenFileName(
                self, "Выберите PDF файл", "", "PDF Files (*.pdf)"
            )
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", e)
            return

        if fname:
            self.file_path.setText(fname)
            doc = fitz.open(fname)
            page_count = len(doc)
            self.status_label.setText(
                f"Файл выбран! В нем содержится <b>{page_count}</b> страниц."
            )
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
        pdf_path = self.file_path.text()
        output_path = self.save_path.text() + "/result.pdf"
        exclude_lines = self.exclude_text.toPlainText().splitlines()

        if not pdf_path:
            QMessageBox.warning(self, "Ошибка", "Выберите PDF файл!")
            return
        if not output_path:
            QMessageBox.warning(self, "Ошибка", "Выберите путь сохранения результата!")
            return

        self.status_label.setText("Обработка...")

        self.worker = PDFWorker(
            pdf_path=pdf_path,
            output_path=output_path,
            exclude=exclude_lines,
            settings=self.settings,
        )

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

    def admin_settings_window(self):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox

        dlg = QDialog(self)
        dlg.setWindowTitle("Глубокие настройки")
        layout = QFormLayout(dlg)

        # Поля настроек
        edits = {}
        for key, val in self.settings.items():
            edits[key] = QLineEdit(str(val))
            if key == "TARGET_W" or key == "TARGET_H":
                layout.addRow(f"{key} (мм)", edits[key])
            elif key == "MAX_REASONABLE_SIZE" or key == "NORMAL_FONT_SIZE":
                layout.addRow(f"{key} (пк)", edits[key])
            else:
                layout.addRow(key, edits[key])

        # Кнопки Сохранить/Отмена
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        float_keys = ["TARGET_W", "TARGET_H", "MAX_REASONABLE_SIZE", "NORMAL_FONT_SIZE"]

        if dlg.exec_() == QDialog.Accepted:
            for key in edits:
                try:
                    if float(edits[key].text()) < 0:
                        raise ValueError
                    if key in float_keys:
                        self.settings[key] = float(edits[key].text())
                    else:
                        self.settings[key] = int(edits[key].text())
                except ValueError:
                    QMessageBox.warning(
                        self, "Ошибка", f"Значение для {key} должно быть положительным"
                    )
                except:
                    QMessageBox.warning(self, "Ошибка", f"Неверное значение для {key}")


def main():
    app = QApplication(sys.argv)
    window = PDFProcessorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
