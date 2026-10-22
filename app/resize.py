import pymupdf  # PyMuPDF

def resize_and_save_pdf(input_pdf, output_pdf, settings):
    mm_to_pt = 72 / 25.4
    target_w = settings["TARGET_W"] * mm_to_pt
    target_h = settings["TARGET_H"] * mm_to_pt

    doc = pymupdf.open(input_pdf)
    resized_doc = pymupdf.open()
    for page in doc:
        newpage = resized_doc.new_page(
            width=target_w, height=target_h
        )  # Создаем новый пустой лист нужного размера
        orig_rect = page.rect  # Получаем размеры исходной страницы
        newpage.show_pdf_page(
            newpage.rect, doc, page.number, clip=orig_rect
        )  # Переносим всю старую страницу на новую
        
    resized_doc.save(output_pdf)
    return output_pdf