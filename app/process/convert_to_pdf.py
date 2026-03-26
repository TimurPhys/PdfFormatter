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

        # Генерируем PDF штатными средствами браузера
        print(box)
        await page.pdf(
            path=output_pdf,
            width=f"{box['width']}px",
            height=f"{box['height']}px",
            print_background=True,  # Чтобы сохранились цвета и фоны
        )
        await browser.close()
