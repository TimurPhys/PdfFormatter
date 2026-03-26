import fitz  ## pymupdf
from pathlib import Path
from html_edit import *

from html_edit import edit_document

# base_dir = os.path.dirname("H:\VisualStudioProjects\\PdfFormatter\\")


async def process_pdf(
    input_pdf: str,
    input_html: str,
    output_dir: str,
    settings: dict,
    progress_cb=None,
):
    # Приводим все пути к абсолютному стандарту
    icons_dir = settings["ICONS_DIR"]
    try:
        if progress_cb:
            progress_cb(10)
            edit_document(input_html, input_pdf, icons_dir, output_dir, settings)

        if progress_cb:

            html_result_path = (Path(output_dir) / "result.html").resolve().as_posix()
            print(html_result_path)
            pdf_result_path = (Path(output_dir) / "result.pdf").resolve()
            await html_to_pdf(html_result_path, pdf_result_path, settings)

            progress_cb(100)
        print("Все этапы успешно завершены!")

    except Exception as e:
        print(f"Произошла ошибка в process_pdf: {e}")
        import traceback

        traceback.print_exc()
    finally:
        tmp_png = os.path.join(output_dir, "datamatrix.png")
        tmp_result = os.path.join(output_dir, "result.html")
        for file_path in [tmp_png, tmp_result]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Файл {file_path} успешно удален.")
                except Exception as e:
                    print(f"Не удалось удалить {file_path}: {e}")
        # УДАЛЯЕМ ПО ПОЛНЫМ ПУТЯМ
