from PyQt5.QtCore import QThread, pyqtSignal
from processor import process_pdf


class PDFWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, pdf_path, output_path, exclude, settings):
        super().__init__()
        self.pdf_path = pdf_path
        self.exclude = exclude
        self.settings = settings
        self.output_path = output_path

    def run(self):
        try:
            print(self.exclude)
            process_pdf(
                input_pdf=self.pdf_path,
                output_pdf=self.output_path,
                exclude_texts=self.exclude,
                settings=self.settings,
                progress_cb=self.progress.emit,
            )
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
