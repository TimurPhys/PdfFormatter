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
    QCheckBox,
)
from PyQt5.QtCore import Qt
from worker import PDFWorker
import ast
from settings.settings_manager import SettingsManager
from protection import check_protection


### ГЛАВНОЕ ОКНО
class PDFProcessorGUI(QWidget):
    def __init__(self):
        super().__init__()  # Вызываем конструктор дочернего класса
        self.setWindowTitle("PDF Processor")  # Даем название окну
        self.settings_manager = SettingsManager()  # Копируем настройки в класс
        # self.settings_manager.drop_settings()
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

        file_layout.addWidget(self.file_label_pdf)
        file_layout.addWidget(self.file_path_pdf)
        file_layout.addWidget(self.browse_btn_pdf)

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
        output_path = self.save_path.text()
        self.settings["EXCEPTIONS"] = self.exclude_text.toPlainText().splitlines()

        if not pdf_path:
            QMessageBox.warning(self, "Ошибка", "Выберите PDF файл!")
            return
        if not output_path:
            QMessageBox.warning(self, "Ошибка", "Выберите путь сохранения результата!")
            return

        self.status_label.setText("Обработка...")

        self.worker = PDFWorker(pdf_path, output_path, self.settings)

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

    def drop_settings(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы действительно хотите сбросить настройки?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            print("Сброс настроек")
            self.settings_manager.drop_settings()
            self.settings = self.settings_manager.load_settings()
            self.settings_window.close()
        else:
            print("Отмена сброса")

    def admin_settings_window(self):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox

        self.settings_window = QDialog(self)
        self.settings_window.setWindowTitle("Глубокие настройки")
        layout = QFormLayout(self.settings_window)

        # Поля настроек
        edits = {}
        for key, val in self.settings.items():
            # if key == "LOGO_SIZE":
            #     val = json.dumps(str(val), ensure_ascii=False)
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
            elif key == "EDIT_WHOLE_PDF":
                row_layout = QHBoxLayout()
                self.cb = QCheckBox(str(key), self)
                self.cb.setChecked(bool(self.settings.get("EDIT_WHOLE_PDF")))
                self.cb.setLayoutDirection(Qt.RightToLeft)
                self.cb.setStyleSheet("margin-left: 0;")
                self.cb.stateChanged.connect(
                    lambda state: [
                        edits["START"].setEnabled(state == 0),
                        edits["END"].setEnabled(state == 0),
                        self.settings.update(
                            {"EDIT_WHOLE_PDF": state == 2}
                        ),  # обновляем настройки сразу
                    ]
                )
                row_layout.addWidget(self.cb)
                row_layout.addStretch()
                layout.addRow(row_layout)
            elif key == "TARGET_W" or key == "TARGET_H":
                layout.addRow(f"{key} (мм)", edits[key])
            elif key == "START" or key == "END":
                edits[key].setEnabled(not self.settings.get("EDIT_WHOLE_PDF", False))
                layout.addRow(key, edits[key])
            else:
                layout.addRow(key, edits[key])

        self.drop_settings_button = QPushButton("Сбросить значения")
        self.drop_settings_button.clicked.connect(self.drop_settings)
        layout.addRow(self.drop_settings_button)

        # Кнопки Сохранить/Отмена
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.settings_window.accept)
        buttons.rejected.connect(self.settings_window.reject)
        layout.addWidget(buttons)

        float_keys = [
            "TARGET_W",
            "TARGET_H",
            "FACTOR",
        ]
        int_keys = ["START", "END"]

        if self.settings_window.exec_() == QDialog.Accepted:
            try:
                for key in edits:
                    if key in float_keys:
                        self.settings[key] = float(edits[key].text())
                    elif key in int_keys:
                        if int(edits[key].text()) <= 0:
                            raise ValueError(
                                "Значения номеров страниц должны быть положительными!"
                            )
                        self.settings[key] = int(edits[key].text())
                    elif key == "LOGO_SIZE":
                        self.settings[key] = ast.literal_eval(edits[key].text())
                    elif key == "EDIT_WHOLE_PDF":
                        continue
                    else:
                        self.settings[key] = edits[key].text()
                self.settings_manager.save_settings(self.settings)
                print(self.settings)
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
