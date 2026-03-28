import cloudconvert
import os


def convert_pdf_to_html(pdf_path, output_dir, settings):
    # Настройка API
    api_key = settings.get("API_KEY")
    cloudconvert.configure(api_key=api_key, sandbox=False)

    # Создание задания
    payload = {
        "tasks": {
            "upload-task": {"operation": "import/upload"},
            "convert": {
                "operation": "convert",
                "input": ["upload-task"],
                "input_format": "pdf",
                "output_format": "html",
                "engine": "mupdf",
                "outline": False,
                "zoom": 1.5,
                "embed_css": True,
                "embed_javascript": True,
                "embed_images": True,
                "embed_fonts": True,
                "split_pages": False,
                "bg_format": "png",
            },
            "export-task": {
                "operation": "export/url",
                "input": ["convert"],
            },
        },
        "tag": "jobbuilder",
    }

    # 3. Загружаем локальный файл
    job = cloudconvert.Job.create(payload=payload)

    upload_task_id = job["tasks"][0]["id"]
    upload_task = cloudconvert.Task.find(id=upload_task_id)

    print(f"--- Загрузка файла: {pdf_path} ---")
    cloudconvert.Task.upload(file_name=pdf_path, task=upload_task)

    print("--- Ожидание завершения... ---")
    finished_job = cloudconvert.Job.wait(id=job["id"])
    print(finished_job)

    export_task = next(t for t in finished_job["tasks"] if t["name"] == "export-task")

    if export_task["status"] == "finished":
        file_info = export_task["result"]["files"][0]
        output_file = os.path.join(output_dir, "output.html")

        cloudconvert.download(url=file_info["url"], filename=output_file)
        print(f"--- Успех! Файл сохранен: {output_file} ---")
    elif export_task["status"] == "error":
        raise Exception("Ошибка запроса на сервер")
    else:
        raise Exception("Неизвестная ошибка")
