import fitz  ## pymupdf
import os
from html_edit import *
from pylibdmtx.pylibdmtx import decode

# === НАСТРОЙКИ ИСХОДНОГО РАЗМЕРА ===
TARGET_W, TARGET_H = 40 * 2.83465, 25 * 2.83465  # 40x25 мм
    

base_dir = os.path.dirname("c:\\Users\\LVG1614\\Documents\\Timurs_Scepanovs_12.b\\Python\\PdfFormatter\\")

# Формируем пути
input_pdf = os.path.join(base_dir, "test", "test_2.pdf")
input_html = os.path.join(base_dir, "test", "test_1.html")
output_dir = os.path.join(base_dir, "result")
edit_html(input_html, input_pdf, output_dir)


def process_pdf(
    input_pdf: str,
    input_docx: str,
    output_pdf: str,
    exclude_texts: list[str],
    settings: dict,
    progress_cb=None,
):
    # Приводим все пути к абсолютному стандарту
    input_pdf = os.path.abspath(input_pdf)
    output_pdf = os.path.abspath(output_pdf)
    input_dir = os.path.dirname(input_pdf)

    # Определяем полные пути временных файлов заранее
    tmp_docx = os.path.join(input_dir, "output_doc.docx")
    tmp_edited_docx = os.path.join(input_dir, "edited_output.docx")
    tmp_edited_pdf = os.path.join(input_dir, "edited_output.pdf")

    try:
        if progress_cb:
            progress_cb(10)

        if progress_cb:
            progress_cb(100)
        print("Все этапы успешно завершены!")

    except Exception as e:
        print(f"Произошла ошибка в process_pdf: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # УДАЛЯЕМ ПО ПОЛНЫМ ПУТЯМ
        for file_path in [tmp_docx, tmp_edited_docx, tmp_edited_pdf]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Файл {file_path} успешно удален.")
                except Exception as e:
                    print(f"Не удалось удалить {file_path}: {e}")
