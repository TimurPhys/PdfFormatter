import fitz  ## pymupdf
from pdf2docx import Converter
from docx import Document
from docx.shared import Pt
from docx2pdf import convert
import os

# === НАСТРОЙКИ ИСХОДНОГО РАЗМЕРА ===
TARGET_W, TARGET_H = 40 * 2.83465, 25 * 2.83465  # 40x25 мм


# === РЕСАЙЗ СТАРОГО PDF ===
def resize_pdf(input_pdf, output_pdf, settings):
    doc = fitz.open(input_pdf)
    resized_doc = fitz.open()

    for page in doc:
        new_page = resized_doc.new_page(
            width=float(settings["TARGET_W"] * 2.83465),
            height=float(settings["TARGET_H"] * 2.83465),
        )

        new_page.show_pdf_page(new_page.rect, doc, page.number)

    resized_doc.save(output_pdf)


# === КОНВЕРТАЦИЯ PDF В DOCX ===
def convert_to_docx(pdf_doc, docx_doc, settings):
    cv = Converter(pdf_file=pdf_doc)
    if settings["EDIT_WHOLE_PDF"] == 1:
        cv.convert(docx_filename=docx_doc)  # Конвертация pdf в docx
    else:
        cv.convert(
            docx_filename=docx_doc, start=settings["START"], end=settings["END"]
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


def edit_docx(docx_doc, TEXT_TO_EXCLUDE, settings):
    doc = Document(docx_doc)
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

    doc.save("edited_output.docx")


def process_pdf(
    input_pdf: str,
    output_pdf: str,
    exclude_texts: list[str],
    settings: dict,
    progress_cb=None,
):
    try:
        convert_to_docx(input_pdf, "output_doc.docx", settings)
        if progress_cb:
            progress_cb(25)
        edit_docx("output_doc.docx", exclude_texts, settings)
        if progress_cb:
            progress_cb(50)
        convert("edited_output.docx", "edited_output.pdf")
        if progress_cb:
            progress_cb(75)
        resize_pdf("edited_output.pdf", output_pdf, settings)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        temp_files = ["output_doc.docx", "edited_output.docx", "edited_output.pdf"]
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"Файл {file} удален.")
        if progress_cb:
            progress_cb(100)
