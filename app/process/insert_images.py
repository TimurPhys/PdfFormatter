import os


def insert_image_to_html(soup, parent_div, rect, output_dir, img_name="datamatrix.png"):
    # 1. Сохраняем байты в файл
    img_path = os.path.join(output_dir, img_name)

    # 2. Вычисляем размеры из Rect
    x0, y0, x1, y1 = rect
    width = x1 - x0
    height = y1 - y0

    # 3. Создаем тег img
    new_img = soup.new_tag("img")
    new_img["src"] = img_path

    # Формируем стиль для точного наложения
    new_img["style"] = (
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


def insert_logo_to_html(soup, parent_div, size, logo_path):
    new_img = soup.new_tag("img")
    new_img["src"] = logo_path

    new_img["style"] = (
        f"position: absolute; "
        f"left: {float(size['x0'])}em; "
        f"top: {float(size['y0'])}em; "
        f"width: {float(size['width'])}pt; "
        f"height: {float(size['height'])}pt; "
        f"z-index: 1000;"
    )
    if parent_div:
        parent_div.append(new_img)
