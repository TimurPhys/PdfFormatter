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
