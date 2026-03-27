from html_edit import *

from html_edit import edit_document
from process.convert_to_pdf import html_to_pdf
from process.request import convert_pdf_to_html

base_dir = os.path.dirname("H:\VisualStudioProjects\\PdfFormatter\\")


async def process_pdf(
    input_pdf: str,
    output_dir: str,
    settings: dict,
    progress_cb=None,
):
    # Приводим все пути к абсолютному стандарту
    icons_dir = settings["ICONS_DIR"]

    try:
        if progress_cb:

            progress_cb(10)
            convert_pdf_to_html(input_pdf, output_dir, settings)

            input_html = os.path.join(output_dir, "output.html")

            progress_cb(30)

            edit_document(input_html, input_pdf, icons_dir, output_dir, settings)
            html_result_path = os.path.join(output_dir, "result.html")
            print(html_result_path)
            pdf_result_path = os.path.join(output_dir, "result.pdf")
            await html_to_pdf(html_result_path, pdf_result_path, settings)

            progress_cb(100)
            print("Все этапы успешно завершены!")

    except Exception as e:
        print(f"Произошла ошибка в process_pdf: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pass
        tmp_png = os.path.join(output_dir, "datamatrix.png")
        tmp_html = os.path.join(output_dir, "output.html")
        tmp_result = os.path.join(output_dir, "result.html")
        for file_path in [tmp_png, tmp_result, tmp_html]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Файл {file_path} успешно удален.")
                except Exception as e:
                    print(f"Не удалось удалить {file_path}: {e}")
        # УДАЛЯЕМ ПО ПОЛНЫМ ПУТЯМ


# input_pdf = os.path.join(base_dir, "test", "test.pdf")
# output_dir = os.path.join(base_dir, "result")
# settings = {
#     "TARGET_W": 40.0,
#     "TARGET_H": 25.0,
#     "START": 1,
#     "END": 1,
#     "EDIT_WHOLE_PDF": True,
#     "FACTOR": 1.22,
#     "EXCEPTIONS": [],
#     "LOGO_SIZE": {"x0": 2.5, "y0": 8, "width": 15, "height": 15},
#     "ICONS_DIR": os.path.join(base_dir, "icons"),
#     "BROWSER": "chrome",
#     "API_KEY": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZTI5MzJhZGQ4OTY2ZjU2N2NkNmUzZjE1MTczMTIwZWFkNThlMjc3N2ZlYTBiZmYzMjIxZjkwM2EzNDM0MzM3ZDg1NThhOTdjYzczMzVjYmQiLCJpYXQiOjE3NzQ2MTgwMTYuMjQxOCwibmJmIjoxNzc0NjE4MDE2LjI0MTgwMSwiZXhwIjo0OTMwMjkxNjE2LjIzNTYwNSwic3ViIjoiNzQ4ODAxOTgiLCJzY29wZXMiOlsidGFzay5yZWFkIiwidGFzay53cml0ZSJdfQ.gznH6fveSpbVpAa6_s1WepP6VLeDr05Orjl3_WJwcRgB7g5W6N4pCIXuZYRbFpbQaGaz2RESjz_FqEjnCuyzAjFhkGAE8zLK0_z64ajy9l5K3hlgVHr_Tfel2rg6JSHDdzLw7w9oT3G3SM03QjGDKDrYEpz3qZIz13Ev_XGxwEuZVDlaw5o48qxAUT7yiG1L2EnX3axg3IduqdZUf70Ao7QJYWS1BsCO0XsWYFRRQ9YC4dcF1xFZocEvVE074BdNP9jskRIHf1qX1qpTWIzKsIXXwKS9GBkW04D--qCeVEbY7KInKUSpsYW3GOv9grp6oXQn0hkCi1ji83x-MKIpvmt89lzia6tUBYl-b7qYz5BlzOeNe-S7IXdLherbJsqg--jEdhlLnNlXnwgYn0Whl89r9x8z41RgfMsPGjgS6kAnDmMLiKjpdpRN8giJiAqtcSyGjBtNUnCZkANu8WsxrwecbEPfDLP13wj_xitSzCHqpv5OKqJbNGQzj1ueUGhhWjswSgAt3G7bnK9NgbbsnH7e9QC7JBexJ1Oi1kS7AIdJ-00MCngXKjrQHyU47UINg3oeHvYZQv4yChncmMwD2A5d4RYvTWJN8t_3fF850ic5E1gwzQ5SZElz3oeQL-_2YedbIkTthmNqmrdnGfxSO6qn-m_k-hrfCkF18VVoy74",
# }

# asyncio.run(process_pdf(input_pdf, output_dir, settings))
