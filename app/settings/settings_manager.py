import json
import os

DEFAULT_SETTINGS = {
    "TARGET_W": 40.0,
    "TARGET_H": 25.0,  # 40x25 мм
    "EDIT_WHOLE_PDF": 1,
    "START": 0,
    "END": 0,
    "FACTOR": 1.2,
    "EXCEPTIONS": [],
    "LOGO_SIZE": {
        "x0": 2.5,
        "y0": 8,
        "width": 15,
        "height": 15,
    },
    "ICONS_DIR": "",
}

app_data_path = os.path.join(os.environ["APPDATA"], "PdfFormatter", "settings.json")


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

    def save_settings(self, new_settings):
        self.settings = new_settings
        dir_path = os.path.dirname(self.filename)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(self.filename, "w", encoding="utf-8") as f:
            # indent=4 делает файл "красивым" и читаемым для человека
            json.dump(self.settings, f, indent=4, ensure_ascii=False)
