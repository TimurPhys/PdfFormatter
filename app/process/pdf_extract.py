import fitz
import os


def extract_image_from_page(pdf_path, page_index, output_dir):
    if not os.path.exists(pdf_path):
        return
    doc = fitz.open(pdf_path)

    page = doc[page_index]
    image_list = page.get_images()

    all_images = []
    for img in image_list:
        xref = img[0]
        rects = page.get_image_rects(xref)
        if rects:
            all_images.append({"xref": xref, "rect": rects[0]})

    if not all_images:
        doc.close()
        return None

    target = min(all_images, key=lambda x: abs(x["rect"].width - x["rect"].height))

    rect = target["rect"]
    base_image = doc.extract_image(target["xref"])
    image_bytes = base_image["image"]

    qr_code_xref = image_list[1][0]
    rect = page.get_image_rects(qr_code_xref)[0]

    base_image = doc.extract_image(qr_code_xref)
    image_bytes = base_image["image"]

    images_directory = os.path.join(output_dir, "images")
    if not os.path.exists(images_directory):
        os.makedirs(images_directory, exist_ok=True)

    with open(
        os.path.join(images_directory, f"datamatrix-{page_index}.png"), "wb"
    ) as f:
        f.write(image_bytes)

    doc.close()
    return rect
