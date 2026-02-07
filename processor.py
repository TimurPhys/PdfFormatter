import fitz  ## pymupdf
from pdf2docx import Converter
from docx import Document
from docx.shared import Pt
from docx2pdf import convert
import os

# === НАСТРОЙКИ ИСХОДНОГО РАЗМЕРА ===
TARGET_W, TARGET_H = 40 * 2.83465, 25 * 2.83465  # 40x25 мм


# === РЕСАЙЗ СТАРОГО PDF ===
def resize_pdf(input_pdf, output_pdf, settings, input_dir):
    doc = fitz.open(input_pdf)
    resized_doc = fitz.open()

    for page in doc:
        new_page = resized_doc.new_page(
            width=float(settings["TARGET_W"] * 2.83465),
            height=float(settings["TARGET_H"] * 2.83465),
        )

        new_page.show_pdf_page(new_page.rect, doc, page.number)

    resized_doc.save(os.path.join(input_dir, output_pdf))


# === КОНВЕРТАЦИЯ PDF В DOCX ===
def convert_to_docx(pdf_doc, docx_doc, settings, input_dir):
    cv = Converter(pdf_file=os.path.join(input_dir, pdf_doc))
    if settings["EDIT_WHOLE_PDF"] == 1:
        cv.convert(docx_filename=docx_doc)  # Конвертация pdf в docx
    else:
        cv.convert(
            docx_filename=os.path.join(input_dir, docx_doc),
            start=settings["START"],
            end=settings["END"],
        )  # Конвертация pdf в docx
    cv.close()


MAX_REASONABLE_SIZE = 6
NORMAL_FONT_SIZE = 7


def get_run_size(run, paragraph, settings):
    # 1. размер run
    if run.font.size:
        size = run.font.size.pt
        if size > settings["MAX_REASONABLE_SIZE"]:
            return settings["NORMAL_FONT_SIZE"]
        return size

    # 2. размер стиля абзаца
    if paragraph.style and paragraph.style.font.size:
        return paragraph.style.font.size.pt

    # 3. fallback (обычно Normal = 11pt)
    return 4


def edit_docx(docx_doc, TEXT_TO_EXCLUDE, settings, input_dir):
    doc = Document(os.path.join(input_dir, docx_doc))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True

                        if any(text in run.text for text in TEXT_TO_EXCLUDE):
                            continue

                        base_size = get_run_size(run, paragraph, settings)
                        if run.font.size:
                            if run.font.size.pt > 10:
                                print("Большой шрифт")
                                print(run.text)
                        run.font.size = Pt(base_size + 1)

    for paragraph in doc.paragraphs:
        if any(text in paragraph.text for text in TEXT_TO_EXCLUDE):
            continue

        for run in paragraph.runs:
            run.bold = True
            run.font.size = Pt(run.font.size.pt + 1)

    doc.save(os.path.join(input_dir, "edited_output.docx"))


def process_pdf(
    input_pdf: str,
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

        # Шаг 1: PDF -> DOCX
        # Передаем уже полный путь tmp_docx
        convert_to_docx(input_pdf, tmp_docx, settings, input_dir)

        if progress_cb:
            progress_cb(30)

        # Шаг 2: EDIT DOCX
        # Убедитесь, что внутри edit_docx вы используете переданные пути!
        edit_docx("output_doc.docx", exclude_texts, settings, input_dir)

        if progress_cb:
            progress_cb(50)

        # Шаг 3: DOCX -> PDF (САМЫЙ ОПАСНЫЙ МОМЕНТ)
        print(f"Конвертируем {tmp_edited_docx}...")
        # Используем нормализованные пути
        convert(os.path.normpath(tmp_edited_docx), os.path.normpath(tmp_edited_pdf))

        if progress_cb:
            progress_cb(75)

        # Шаг 4: RESIZE
        resize_pdf(tmp_edited_pdf, output_pdf, settings, input_dir)

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
