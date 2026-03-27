from bs4 import BeautifulSoup
import cssutils
import os
import re

from process.html_text_edit import edit_span_style
from process.pdf_extract import extract_image_from_page
from process.insert_images import insert_image_to_html, insert_logo_to_html


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

    pages = soup.find_all("div", id=re.compile(r"^page"))

    ### --- Редактирование текста ---- ###
    for page in pages:
        page["style"] += "; padding: 2px;"
        for span in page.find_all("span"):
            has_exception = False
            new_style = "; font-weight: 600 !important;"

            for exception in exceptions:
                if exception in span.text:
                    has_exception = True
            if has_exception:
                continue

            span_style = span.get("style")
            style = cssutils.parseStyle(span_style)
            font_size = float(style.getPropertyValue("font-size").replace("pt", ""))
            new_style += f"font-size: {font_size * factor}pt !important;"

            edit_span_style(span, new_style)
    # ### --- Редактирование текста ---- ###

    # ### --- Вставка картинок ---- ###
    for page in pages:
        page_number = int(page.get("id").replace("page", "")) - 1
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

    # ### --- Вставка картинок ---- ###

    # # # Сохраняем
    output_path = os.path.join(output_dir, "result.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
