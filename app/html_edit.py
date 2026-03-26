from bs4 import BeautifulSoup
import tinycss2
import os
import io
import re

from process.html_text_edit import get_font_size, edit_span_style, useful_selectors
from process.pdf_extract import extract_image_from_page
from process.insert_images import insert_image_to_html, insert_logo_to_html
from process.convert_to_pdf import html_to_pdf


def edit_document(
    html_path: str,
    pdf_path: str,
    icons_path: str,
    output_dir: str,
    settings: dict,
):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    factor = settings["FACTOR"]
    exceptions = settings["EXCEPTIONS"]
    logo_size = settings["LOGO_SIZE"]

    ### --- Редактирование текста ---- ###
    style_text = soup.find("style").string
    rules = tinycss2.parse_stylesheet(
        style_text, skip_comments=True, skip_whitespace=True
    )

    for span in soup.find_all("span"):
        has_exception = False
        new_style = "font-weight: 600 !important;"
        for exception in exceptions:
            if exception in span.text:
                has_exception = True

        if not has_exception:
            font_size = float(get_font_size(span, rules))
            new_style += f"font-size: {font_size * factor}em;"
        edit_span_style(span, new_style)
    useful_selectors.clear()
    ### --- Редактирование текста ---- ###

    ### --- Вставка картинок ---- ###
    pages = soup.find_all("div", id=re.compile(r"^page"))
    for page in pages:
        page_number = int(page.get("id").replace("page_", ""))
        rect = extract_image_from_page(
            pdf_path, page_number, output_dir
        )  # Извлекаем картинку

        for img in page.find_all("img"):
            parent_div = img.find_parent("div")
            img.decompose()
            EAC_icon = os.path.join(icons_path, "EAC-logo.png")
            insert_logo_to_html(
                soup, parent_div, logo_size, EAC_icon
            )  # Вставляем лого EAC
            insert_image_to_html(
                soup, parent_div, rect, output_dir
            )  # Вставляем извлеченную картинку

    ### --- Вставка картинок ---- ###

    # # Сохраняем
    output_path = os.path.join(output_dir, "result.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
