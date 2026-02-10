import os
import sys
import json
import hashlib
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QLineEdit

CONFIG_NAME = "sys_cache.dat"

# пароль: 12345
PASSWORD_HASH = "5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5"


def get_exe_path():
    # корректно работает и в .exe
    return os.path.abspath(sys.executable)


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def get_config_path():
    # прячем конфиг в AppData
    base = os.getenv("LOCALAPPDATA") or os.getcwd()
    folder = os.path.join(base, "PDFProcessor")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, CONFIG_NAME)


def load_saved_path():
    cfg = get_config_path()
    if not os.path.exists(cfg):
        return None
    with open(cfg, "r") as f:
        return json.load(f).get("path")


def save_path(path):
    cfg = get_config_path()
    with open(cfg, "w") as f:
        json.dump({"path": path}, f)


def check_protection(parent=None) -> bool:
    current_path = get_exe_path()
    saved_path = load_saved_path()

    # если путь изменился или он еще не сохранился
    if saved_path != current_path or save_path is None:
        pwd, ok = QInputDialog.getText(
            parent,
            "Защита",
            "Введите пароль:",
            QLineEdit.Password,
        )

        if not ok or hash_text(pwd) != PASSWORD_HASH:
            QMessageBox.critical(
                parent,
                "Доступ запрещён",
                "Неверный пароль. Программа будет закрыта.",
            )
            return False

        save_path(current_path)

    return True
