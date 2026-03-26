from bs4 import BeautifulSoup
import fitz  ## pymupdf
import tinycss2
import os
import sys
import io
import re

# Это заставит консоль принимать любые символы (кириллицу, латышский и т.д.)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')



def insert_image_to_html(soup, parent_div, image_bytes, rect, output_dir, img_name="datamatrix.png"):
    # 1. Сохраняем байты в файл
    img_path = os.path.join(output_dir, img_name)
    with open(img_path, "wb") as f:
        f.write(image_bytes)

    # 2. Вычисляем размеры из Rect
    x0, y0, x1, y1 = rect
    width = x1 - x0
    height = y1 - y0

    # 3. Создаем тег img
    new_img = soup.new_tag("img")
    new_img['src'] = os.path.join(output_dir, img_name)  # Если HTML и картинка в одной папке
    
    # Формируем стиль для точного наложения
    new_img['style'] = (
        f"position: absolute; "
        f"left: {x0}pt; "
        f"top: {y0}pt; "
        f"width: {width}pt; "
        f"height: {height}pt; "
        f"z-index: 1000;"
    )

    # 4. Ищем нужную страницу (например, первую) и добавляем туда
    # Если ваш HTML разбит на <div id="page0">, <div id="page1"> и т.д.
    if parent_div:
        parent_div.append(new_img)

    return soup

def extract_image_from_page(pdf_path, page_index):
    if not os.path.exists(pdf_path):
        return

    doc = fitz.open(pdf_path)

    page = doc[page_index]
    image_list = page.get_images()

    qr_code_xref = image_list[1][0]
    rect = page.get_image_rects(qr_code_xref)[0]

    base_image = doc.extract_image(qr_code_xref)
    image_bytes = base_image["image"]

    doc.close()
    return image_bytes, rect


useful_selectors = {}
def get_font_size(span, rules):
    classes = span.get("class", "")
    if not classes:
        return None

    font_class = classes[0]

    for selector, font_size in useful_selectors.items():
        if font_class in selector:
            return font_size

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

                useful_selectors[selector] = font_size
                return font_size

def edit_span_style(span, new_style):
    span_style = span.get("style")
    if span_style:
        span_style += new_style
        span["style"] = span_style
    else:
        span["style"] = new_style

def edit_html(html_path: str, pdf_path: str, output_dir: str, exceptions: list = [], factor: float = 1.2):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

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
    # Сохраняем
    useful_selectors.clear()

    pages = soup.find_all("div", id=re.compile(r"^page"))

    for page in pages:
        page_number = int(page.get("id").replace("page_", ""))
        image, rect = extract_image_from_page(pdf_path, page_number)

        for img in page.find_all('img'):
            parent_div = img.find_parent("div")
            img.decompose()
            insert_image_to_html(soup, parent_div, image, rect, output_dir)

    with open("label_bold.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
