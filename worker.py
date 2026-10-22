from PyQt5.QtCore import QThread, pyqtSignal
from processor import process_pdf


# Создаем класс задачи, которая будет выполняться
class PDFWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, input, output_path, settings): ## Конструктор класса
        super().__init__()
        self.input = input
        self.output_path = output_path
        self.settings = settings

    def run(self):
        try:
            print(f"Текущие настройки: {self.settings}")
            process_pdf(
                self.input,
                self.output_path,
                self.settings,
                self.progress.emit
            )
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
