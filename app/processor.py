from pathlib import Path
from html_edit import *
import asyncio

from html_edit import edit_document
from process.request import convert_pdf_to_html

base_dir = os.path.dirname("H:\VisualStudioProjects\\PdfFormatter\\")


async def process_pdf(
    input_pdf: str,
    output_dir: str,
    settings: dict,
    progress_cb=None,
):
    # Приводим все пути к абсолютному стандарту
    icons_dir = settings["ICONS_DIR"]

    try:
        # if progress_cb:
        #     progress_cb(10)
        # convert_pdf_to_html(input_pdf, output_dir, settings)

        input_html = os.path.join(output_dir, "output.html")

        # progress_cb(30)

        edit_document(input_html, input_pdf, icons_dir, output_dir, settings)

        # if progress_cb:
        #     html_result_path = (Path(output_dir) / "result.html").resolve().as_posix()
        #     print(html_result_path)
        #     pdf_result_path = (Path(output_dir) / "result.pdf").resolve()
        #     await html_to_pdf(html_result_path, pdf_result_path, settings)

        # progress_cb(100)
        # print("Все этапы успешно завершены!")

    except Exception as e:
        print(f"Произошла ошибка в process_pdf: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pass
        # tmp_png = os.path.join(output_dir, "datamatrix.png")
        # tmp_result = os.path.join(output_dir, "result.html")
        # for file_path in [tmp_png, tmp_result]:
        #     if os.path.exists(file_path):
        #         try:
        #             os.remove(file_path)
        #             print(f"Файл {file_path} успешно удален.")
        #         except Exception as e:
        #             print(f"Не удалось удалить {file_path}: {e}")
        # УДАЛЯЕМ ПО ПОЛНЫМ ПУТЯМ


input_pdf = os.path.join(base_dir, "test", "test.pdf")
output_dir = os.path.join(base_dir, "result")
settings = {
    "TARGET_W": 40.0,
    "TARGET_H": 25.0,
    "START": 1,
    "END": 1,
    "EDIT_WHOLE_PDF": True,
    "FACTOR": 1.2,
    "EXCEPTIONS": [],
    "LOGO_SIZE": {"x0": 2.5, "y0": 8, "width": 15, "height": 15},
    "ICONS_DIR": "",
    "BROWSER": "chrome",
    "API_KEY": "",
}

asyncio.run(process_pdf(input_pdf, output_dir, settings))
