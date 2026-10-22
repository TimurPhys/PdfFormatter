import sys
import pymupdf
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QInputDialog,
)
import hashlib
import settings as s
from worker import PDFWorker


### ГЛАВНОЕ ОКНО
class PDFProcessorGUI(QWidget):
    def __init__(self):
        super().__init__()  # Вызываем конструктор дочернего класса
        self.setWindowTitle("PDF Processor")  # Даем название окну
        self.settings = s.load_or_create_settings()  # Копируем настройки в класс

        if not self.settings.get("IS_ACTIVATED", False):
            if not self.check_password_dialog():
                sys.exit(0)

        self.init_ui()  # Создаем графический интерфейс

    def init_ui(self):
        layout = (
            QVBoxLayout()
        )  # Фундамент интерфейса # <---------------------------------------------------------

        # --- Выбор файла ---
        file_layout = (  # <---------------------------------------------------------
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
        save_layout = (
            QHBoxLayout()
        )  # <---------------------------------------------------------

        self.save_label = QLabel("Выберите путь сохранения PDF файла:")  # Тупо текст
        self.save_path = QLineEdit()  # Однострочный ввод
        self.save_path_btn = QPushButton("Обзор")  # Кнопка "Обзор"
        self.save_path_btn.clicked.connect(self.browse_save_path)
        save_layout.addWidget(self.save_label)
        save_layout.addWidget(self.save_path)
        save_layout.addWidget(self.save_path_btn)

        # --- Кнопки ---
        btn_layout = (
            QHBoxLayout()
        )  # <---------------------------------------------------------
        # Горизонтальный layout

        self.process_btn = QPushButton("Обработать")
        self.process_btn.clicked.connect(self.process_file)
        self.admin_btn = QPushButton("⚙ Настройки")
        self.admin_btn.clicked.connect(self.settings_window)
        btn_layout.addWidget(self.process_btn)
        btn_layout.addWidget(self.admin_btn)

        # --- Прогресс ---
        self.progress = (
            QProgressBar()
        )  # <---------------------------------------------------------

        self.progress.setValue(0)
        self.progress.setVisible(False)

        # --- Статус ---
        self.status_label = QLabel(
            "Выберите файл"
        )  # <---------------------------------------------------------

        # --- Сборка ---
        layout.addLayout(file_layout)
        layout.addLayout(save_layout)
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
            doc = pymupdf.open(fname)
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
        input_path = self.file_path.text()
        output_path = self.save_path.text()

        if not input_path:  # Проверка на то, что поля не пустые
            QMessageBox.warning(self, "Ошибка", "Выберите PDF файл!")
            return
        if not output_path:
            QMessageBox.warning(self, "Ошибка", "Выберите путь сохранения результата!")
            return

        self.status_label.setText("Обработка...")
        self.status_label.setStyleSheet("color: green")
        self.worker = PDFWorker(input_path, output_path, self.settings)

        #### Подготовка к запуску worker --- начало ####
        self.progress.setVisible(True)  # Подключаем progress-bar
        self.progress.setValue(0)
        self.worker.progress.connect(self.progress.setValue)
        ## worker будет передавать значения по мере выполнения в progress-bar

        self.worker.finished.connect(
            self.on_finished
        )  # При успешном выполнении вызываем функцию on_finished()
        self.worker.error.connect(
            self.on_error
        )  # При провальном выполнении вызываем функцию on_error()
        #### Подготовка к запуску worker  ---- конец ####
        self.worker.start()  ## Запускаем worker

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

    def dump_settings(self, dlg):
        s.dump_settings()
        self.settings = s.load_or_create_settings()
        QMessageBox.information(self, "Сброс", "Настройки сброшены!")
        dlg.close()

    def settings_window(self):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox

        dlg = QDialog(self)
        dlg.setWindowTitle("Настройки")
        layout = QFormLayout(dlg)
        print("-> Диалоговое окно создано.")

        # Поля настроек
        edits = {}
        for key, val in self.settings.items():
            match key:
                case "TARGET_W" | "TARGET_H":
                    edits[key] = QLineEdit(str(val))
                    text = "Ширина" if key == "TARGET_W" else "Высота"
                    layout.addRow(text + " (мм)", edits[key])
                case "SCALE":
                    edits[key] = QLineEdit(str(val))
                    layout.addRow("Масштаб", edits[key])
                case "IS_ACTIVATED":
                    activation_layout = QHBoxLayout()
                    status_label = QLabel("Активировано" if val else "Не активировано")
                    color = "green" if val else "red"
                    status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
                    self.dump_settings_button = QPushButton("Сбросить настройки")
                    self.dump_settings_button.clicked.connect(lambda: self.dump_settings(dlg))
                    activation_layout.addWidget(status_label)
                    activation_layout.addWidget(self.dump_settings_button)

        layout.addRow(activation_layout)

        # Кнопки Сохранить/Отмена
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        result = dlg.exec_()  # Отображаем окно
        no_error = True
        if result == QDialog.Accepted:  # Нажата кнопка ок, т.е. применить настройки
            for key in edits:
                if key in s.float_keys:
                    try:
                        d_number = float(edits[key].text())
                        if d_number <= 0:
                            raise ValueError
                        self.settings[key] = d_number
                    except ValueError:
                        no_error = False
                        QMessageBox.warning(
                            self,
                            "Ошибка",
                            f"Значение для {key} должно быть положительным и являться десятичным!",
                        )
                elif key in s.int_keys:
                    try:
                        int_number = int(edits[key].text())
                        if int_number <= 0:
                            raise ValueError
                        self.settings[key] = int_number
                    except ValueError:
                        no_error = False
                        QMessageBox.warning(
                            self,
                            "Ошибка",
                            f"Значение для {key} должно быть положительным и являться целым!",
                        )
            if no_error:
                s.save_settings(self.settings)

    def check_password_dialog(self):
        while True:
            # Вызываем диалоговое окно ввода текста с маскированием символов (пароль)
            password, ok = QInputDialog.getText(
                self,
                "Активация",
                "Введите пароль для запуска:",
                QLineEdit.Password,
            )

            # Если пользователь закрыл окно или нажал Отмена
            if not ok:
                return False

            # Проверяем пароль
            user_input_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
            if user_input_hash == s.password_hash:
                # Сохраняем статус активации в настройки
                self.settings["IS_ACTIVATED"] = True
                s.save_settings(self.settings)  # Сохраняем в JSON
                return True
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Неверный пароль! Попробуйте снова."
                )


def main():
    print("Запуск!")
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("PDF-Formatter-GUI")
        window = PDFProcessorGUI()
        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        print(f"ОШИБКА ПРИ ЗАПУСКЕ: {e}")


if __name__ == "__main__":
    main()
