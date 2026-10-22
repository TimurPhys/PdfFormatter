import os
import json

# Актуальные настройки по умолчанию
default_settings = {"TARGET_W": 40, "TARGET_H": 25, "SCALE": 1.1, "IS_ACTIVATED": False}
float_keys = ["SCALE"]
int_keys = ["TARGET_W", "TARGET_H"]
password_hash = "5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5"

def get_settings_file_path():
    appdata = os.getenv('APPDATA')
    folder = os.path.join(appdata, "PDFProcessorGUI")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, 'settings.json')

def dump_settings():
    path = get_settings_file_path()
    if os.path.exists(path):
        os.remove(path)
        print("Настройки скинуты до заводских!")

def load_or_create_settings():
    path = get_settings_file_path()
    
    # Сценарий 1: Файла вообще нет (первый запуск)
    if not os.path.exists(path):
        print("Файл настроек не найден. Создаем новый по умолчанию...")
        save_settings(default_settings)
        return default_settings.copy()
    
    # Сценарий 2: Файл существует, пробуем прочитать
    try:
        with open(path, 'r', encoding='utf-8') as f:
            user_settings = json.load(f)
            
        # Сценарий 3: Проверка на «устаревшую» структуру (миграция)
        updated = False
        for key in default_settings.keys():
            if key not in user_settings: # Если стандратного ключа нет в файле - удаляем старый файл настроек
                updated = True
                break
                
        if updated:
            print("Обнаружены новые параметры в настройках. Удаляем старые настройки и создаем новый файл.")
            dump_settings()
            save_settings(default_settings)
            
        return user_settings

    except Exception as e:
        print(f"Ошибка чтения старого файла настроек: {e}. Пересоздаем заново.")
        # Если файл поврежден (битый JSON), просто перезаписываем его дефолтом
        save_settings(default_settings)
        return default_settings.copy()

def save_settings(settings_dict):
    path = get_settings_file_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(settings_dict, f, ensure_ascii=False, indent=4)