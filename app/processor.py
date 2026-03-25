import fitz  ## pymupdf
import os
import re
import tinycss2
from bs4 import BeautifulSoup

# === НАСТРОЙКИ ИСХОДНОГО РАЗМЕРА ===
TARGET_W, TARGET_H = 40 * 2.83465, 25 * 2.83465  # 40x25 мм


def extract_image(pdf_path, output_dir):
    if not os.path.exists(pdf_path):
        return

    doc = fitz.open(pdf_path)

    for page_index in range(2):
        page = doc[page_index]
        image_list = page.get_images()

        if image_list:
            print(f"--- Страница {page_index + 1} ---")

        # 1. Проверяем аннотации (иногда логотипы вставляют как штампы)

        for img_index, img in enumerate(image_list):
            xref = img[0]  # Индекс объекта в PDF

            # 1. Достаем само изображение в максимальном качестве
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            # Сохраняем файл
            img_name = f"p{page_index+1}_img{img_index+1}.{image_ext}"
            with open(os.path.join(output_dir, img_name), "wb") as f:
                f.write(image_bytes)

            # 2. Получаем координаты (BBox) изображения на странице
            # Одно изображение может использоваться в разных местах, поэтому ищем все вхождения
            image_rects = page.get_image_rects(xref)

            for rect in image_rects:
                print(f"Картинка {img_name}:")
                print(f"  - Координаты (x0, y0, x1, y1): {rect}")
                print(f"  - Ширина: {rect.width}, Высота: {rect.height}")
                print(
                    f"  - Путь: {os.path.abspath(os.path.join(output_dir, img_name))}"
                )

    doc.close()


def scale_font_size(style_str, factor=1.1):
    """Находит font-size в строке стиля и увеличивает его."""
    if not style_str:
        return f"font-weight: bold; font-size: {factor}em;"  # Дефолт, если стиля нет

    # Регулярка ищет число и единицы измерения (px, pt, em, %)
    match = re.search(r"font-size:\s*(\d+\.?\d*)(px|pt|em|%)", style_str)

    if match:
        old_size = float(match.group(1))
        unit = match.group(2)
        new_size = round(old_size * factor, 2)
        # Заменяем старый размер на новый
        style_str = re.sub(
            r"font-size:\s*[^;]+", f"font-size: {new_size}{unit}", style_str
        )
    else:
        # Если font-size не был указан явно, добавляем его (базовый 10pt -> 11pt)
        style_str += f"; font-size: 1.1em;"

    # Добавляем жирность, если её нет
    if "font-weight" not in style_str:
        style_str += "; font-weight: bold;"
    else:
        style_str = re.sub(r"font-weight:\s*[^;]+", "font-weight: bold", style_str)

    return style_str


def get_font_size(span, rules):
    classes = span.get("class", "")
    if not classes:
        return None

    font_class = classes[0]

    for rule in rules:
        if hasattr(rule, "prelude"):
            selector = "".join(
                token.value for token in rule.prelude if hasattr(token, "value")
            )
            if font_class in selector:
                styles = {}
                content = "".join(token.serialize() for token in rule.content)
                for item in content.split(";"):
                    if ":" in item:
                        key, value = item.split(":", 1)
                        styles[key.strip()] = value.strip()

                font_size = styles.get("font-size").replace("em", "")
                return font_size


def edit_html(html_path: str, output_dir: str, exceptions: str):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    style_text = soup.find("style").string
    rules = tinycss2.parse_stylesheet(
        style_text, skip_comments=True, skip_whitespace=True
    )

    for span in soup.find_all("span"):
        font_size = get_font_size(span, rules)
        print(font_size)

    # Сохраняем
    with open("label_bold.html", "w", encoding="utf-8") as f:
        # prettify иногда ломает верстку с absolute позиционированием,
        # лучше использовать str(soup)
        f.write(str(soup))


input_pdf = os.path.abspath("test_.pdf")
input_html = os.path.abspath("test_.html")
output_dir = os.path.abspath("result")
# extract_image(input_pdf, output_dir)
edit_html(input_html, output_dir, "")


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
