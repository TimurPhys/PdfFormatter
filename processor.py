import pymupdf  # pymupdf
from resize import resize_and_save_pdf
import os

def process_pdf(input_pdf, output_path, settings, progress):
    resized_pdf_path = resize_and_save_pdf(
        input_pdf, output_path + "/resized.pdf", settings
    )
    progress(50)

    # Получаем нужные размеры документа и коэффициент масштабирования
    mm_to_pt = 72 / 25.4
    target_w = settings["TARGET_W"] * mm_to_pt
    target_h = settings["TARGET_H"] * mm_to_pt
    scale = settings["SCALE"]  

    resized_doc = pymupdf.open(resized_pdf_path)
    result_doc = pymupdf.open()

    pages = len(resized_doc)
    for index, page in enumerate(resized_doc):
        progress(int((index + 1) / pages * 100))

        newpage = result_doc.new_page(width=target_w, height=target_h)

        center_x = page.rect.width / 2
        center_y = page.rect.height / 2

        # Сначала переносим всю страницу целиком (как подложку/фон со всеми рамками и shapes),
        # чтобы фоновые линии и дизайн точно не пропали.
        newpage.show_pdf_page(newpage.rect, resized_doc, page.number)

        def scale_coords_with_bounds(x0, y0, x1, y1):
            w = (x1 - x0) * scale
            h = (y1 - y0) * scale
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2

            new_cx = center_x + (cx - center_x) * scale
            new_cy = center_y + (cy - center_y) * scale

            nx0 = new_cx - w / 2
            ny0 = new_cy - h / 2
            nx1 = new_cx + w / 2
            ny1 = new_cy + h / 2

            # ПРОВЕРКА И КОРРЕКТИРОВКА ГРАНИЦ (чтобы не выходило за пределы заданной рамки)
            # Отступаем хотя бы 1 мм от краев (приблизительно 2.8 пункта)
            padding = 2.8

            if nx0 < padding:
                nx1 += padding - nx0  # Сдвигаем вправо
                nx0 = padding
            if nx1 > target_w - padding:
                nx0 -= nx1 - (target_w - padding)  # Сдвигаем влево
                nx1 = target_w - padding

            if ny0 < padding:
                ny1 += padding - ny0  # Сдвигаем вниз
                ny0 = padding
            if ny1 > target_h - padding:
                ny0 -= ny1 - (target_h - padding)  # Сдвигаем вверх
                ny1 = target_h - padding

            target_rect = pymupdf.Rect(nx0, ny0, nx1, ny1)
            source_rect = pymupdf.Rect(x0, y0, x1, y1)
            return target_rect, source_rect

        # 1. Собираем и закрашиваем старый текст
        text_blocks = []
        for b in page.get_text("blocks"):
            if b[6] == 0:
                x0, y0, x1, y1 = b[0], b[1], b[2], b[3]
                text_blocks.append((x0, y0, x1, y1))
                white_rect = pymupdf.Rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
                newpage.draw_rect(white_rect, color=(1, 1, 1), fill=(1, 1, 1))

        # 2. Собираем и закрашиваем старые картинки
        image_coords = []
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            for r in page.get_image_rects(xref):
                x0, y0, x1, y1 = r.x0, r.y0, r.x1, r.y1
                image_coords.append((x0, y0, x1, y1))
                white_rect = pymupdf.Rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
                newpage.draw_rect(white_rect, color=(1, 1, 1), fill=(1, 1, 1))

        # 3. Накладываем увеличенные картинки с учетом границ
        for coords in image_coords:
            target_rect, source_rect = scale_coords_with_bounds(
                coords[0], coords[1], coords[2], coords[3]
            )
            newpage.show_pdf_page(
                target_rect, resized_doc, page.number, clip=source_rect
            )

        # 4. Накладываем увеличенный текст с учетом границ
        planned_rects = []
        for coords in text_blocks:
            target_rect, source_rect = scale_coords_with_bounds(
                coords[0], coords[1], coords[2], coords[3]
            )
            planned_rects.append({
                "target": target_rect,
                "source": source_rect
            })

        resolved_rects = []
        padding = 2.8 ## Оступ от края
        for planned_rect in planned_rects:
            planned_rect_item = planned_rect["target"]
            for resolved_rect in resolved_rects:
                resolved_rect_item = resolved_rect["target"]

                if (planned_rect_item.intersects(resolved_rect_item)): ## Найдено пересечение
                    intersection = planned_rect_item & resolved_rect_item
                    print(f"Есть пересечение и его высота: {intersection.height}")
                    shift_y = intersection.height + 1 # Насколько надо сдвинуть по y
                    if (planned_rect_item.y1 + shift_y >= target_h - padding): ## Если выходим за нижнюю границу
                        if (resolved_rect_item.y0 - shift_y >= 0): # Делаем сдвиг вверх только, если есть место наверху
                            print("Сделан свдиг вверх")
                            # resolved_rect["target"] = pymupdf.Rect(
                            #     resolved_rect_item.x0, 
                            #     resolved_rect_item.y0 - shift_y, 
                            #     resolved_rect_item.x1, 
                            #     resolved_rect_item.y1 - shift_y
                            # )
                            resolved_rect["target"] -= (0, shift_y, 0, shift_y)
                    else:
                        print("Сделан свдиг вниз")
                        # planned_rect["target"] = pymupdf.Rect(
                        #     planned_rect_item.x0, 
                        #     planned_rect_item.y0 + shift_y, 
                        #     planned_rect_item.x1, 
                        #     planned_rect_item.y1 + shift_y
                        # )
                        planned_rect["target"] += (0, shift_y, 0, shift_y)

            resolved_rects.append(planned_rect)

        for item in resolved_rects:
            t_rect = item["target"]
            s_rect = item["source"]
            newpage.show_pdf_page(t_rect, resized_doc, page.number, clip=s_rect)

    result_doc.save(output_path + "/result.pdf")
    result_doc.close()
    resized_doc.close()

    file_to_delete = output_path + "/resized.pdf"
    if os.path.exists(file_to_delete):
        try:
            os.remove(file_to_delete)
            print(f"Файл {file_to_delete} успешно удален.")
        except Exception as e:
            print(f"Не удалось удалить файл: {e}")
