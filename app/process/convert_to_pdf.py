from playwright.async_api import async_playwright


async def html_to_pdf(html_path, output_pdf, settings):
    print(html_path)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f"file:///{html_path}", wait_until="networkidle")

        # Добавляем CSS прямо "на лету"
        # Говорим браузеру: перед каждым div с id="page..." начинай новую страницу
        await page.add_style_tag(
            content="""
            div[id^="page"] {
                break-before: page;
                margin: 0 !important;
                page-break-before: always;
            }
            body { 
                margin: 0 !important; 
                padding: 0 !important; 
                -webkit-print-color-adjust: exact;
            }
        """
        )
        div = await page.wait_for_selector("div[id^='page']", timeout=5000)
        if div:
            box = await div.bounding_box()
            if box:
                print(f"Ширина: {box['width']}, Высота: {box['height']}")
            else:
                print("Элемент найден, но он не имеет визуальных размеров (скрыт)")
        else:
            print("Ошибка: Элемент не найден на странице в течение 5 секунд")

        scale = calculate_scale(settings, box)

        # Генерируем PDF штатными средствами браузера
        await page.pdf(
            path=output_pdf,
            width=f"{box.get('width')*scale}px",
            height=f"{box.get('height')*scale}px",
            scale=scale,
            print_background=True,  # Чтобы сохранились цвета и фоны
        )
        await browser.close()


def calculate_scale(settings, box):
    target_width_px = settings.get("TARGET_W") * 3.78
    target_height_px = settings.get("TARGET_H") * 3.78

    current_width_px = box.get("width")
    current_height_px = box.get("height")

    if not current_width_px or not current_height_px:
        return 1.0

    width_scale = round(target_width_px / current_width_px, 2)
    height_scale = round(target_height_px / current_height_px, 2)

    return round(min(width_scale, height_scale), 2)


# asyncio.run(
#     html_to_pdf(
#         os.path.join("result", "result.html"),
#         os.path.join("result", "result.pdf"),
#         DEFAULT_SETTINGS,
#     )
# )
