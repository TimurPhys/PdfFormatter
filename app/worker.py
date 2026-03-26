from PyQt5.QtCore import QThread, pyqtSignal
from processor import process_pdf
import asyncio

class PDFWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, input_pdf, input_html, output_path, settings):
        super().__init__()
        self.input_pdf = input_pdf
        self.input_html = input_html
        self.settings = settings
        self.output_path = output_path

    def run(self):
        try:
            asyncio.run(process_pdf(
                self.input_pdf,
                self.input_html,
                self.output_path,
                self.settings,
                self.progress.emit,
            ))
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
