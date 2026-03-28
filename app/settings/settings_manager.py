import json
import sys
import os

DEFAULT_SETTINGS = {
    "TARGET_W": 40.0,
    "TARGET_H": 25.0,  # 40x25 мм
    "START": 1,
    "END": 1,
    "EDIT_WHOLE_PDF": True,
    "FACTOR": 1.2,
    "EXCEPTIONS": [],
    "LOGO_SIZE": {
        "x0": 2.5,
        "y0": 8,
        "width": 15,
        "height": 15,
    },
    "ICONS_DIR": "",
    "BROWSER": "chrome",
    "API_KEY": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZTI5MzJhZGQ4OTY2ZjU2N2NkNmUzZjE1MTczMTIwZWFkNThlMjc3N2ZlYTBiZmYzMjIxZjkwM2EzNDM0MzM3ZDg1NThhOTdjYzczMzVjYmQiLCJpYXQiOjE3NzQ2MTgwMTYuMjQxOCwibmJmIjoxNzc0NjE4MDE2LjI0MTgwMSwiZXhwIjo0OTMwMjkxNjE2LjIzNTYwNSwic3ViIjoiNzQ4ODAxOTgiLCJzY29wZXMiOlsidGFzay5yZWFkIiwidGFzay53cml0ZSJdfQ.gznH6fveSpbVpAa6_s1WepP6VLeDr05Orjl3_WJwcRgB7g5W6N4pCIXuZYRbFpbQaGaz2RESjz_FqEjnCuyzAjFhkGAE8zLK0_z64ajy9l5K3hlgVHr_Tfel2rg6JSHDdzLw7w9oT3G3SM03QjGDKDrYEpz3qZIz13Ev_XGxwEuZVDlaw5o48qxAUT7yiG1L2EnX3axg3IduqdZUf70Ao7QJYWS1BsCO0XsWYFRRQ9YC4dcF1xFZocEvVE074BdNP9jskRIHf1qX1qpTWIzKsIXXwKS9GBkW04D--qCeVEbY7KInKUSpsYW3GOv9grp6oXQn0hkCi1ji83x-MKIpvmt89lzia6tUBYl-b7qYz5BlzOeNe-S7IXdLherbJsqg--jEdhlLnNlXnwgYn0Whl89r9x8z41RgfMsPGjgS6kAnDmMLiKjpdpRN8giJiAqtcSyGjBtNUnCZkANu8WsxrwecbEPfDLP13wj_xitSzCHqpv5OKqJbNGQzj1ueUGhhWjswSgAt3G7bnK9NgbbsnH7e9QC7JBexJ1Oi1kS7AIdJ-00MCngXKjrQHyU47UINg3oeHvYZQv4yChncmMwD2A5d4RYvTWJN8t_3fF850ic5E1gwzQ5SZElz3oeQL-_2YedbIkTthmNqmrdnGfxSO6qn-m_k-hrfCkF18VVoy74",
}


def get_project_root():
    # Если приложение собрано в .exe через PyInstaller
    if getattr(sys, "frozen", False):
        # sys._MEIPASS — это временная папка, куда PyInstaller распаковывает ресурсы
        # Но настройки нам нужно хранить РЯДОМ с .exe, а не во временной папке
        return os.path.dirname(sys.executable)
    else:
        # Если запускаем как обычный .py скрипт
        return os.path.dirname(os.path.abspath(__file__))


root = get_project_root()
app_data_path = os.path.join(root, "settings.json")


class SettingsManager:
    def __init__(self, filename=app_data_path):
        self.filename = filename
        self.settings = self.load_settings()

    def load_settings(self):
        # Если файл существует, читаем его
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        # Если файла нет, возвращаем значения по умолчанию
        return DEFAULT_SETTINGS

    def drop_settings(self):
        dir_path = os.path.dirname(self.filename)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)

    def save_settings(self, new_settings):
        self.settings = new_settings
        dir_path = os.path.dirname(self.filename)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(self.filename, "w", encoding="utf-8") as f:
            # indent=4 делает файл "красивым" и читаемым для человека
            json.dump(self.settings, f, indent=4, ensure_ascii=False)
        print("Настройки успешно сохранены")
