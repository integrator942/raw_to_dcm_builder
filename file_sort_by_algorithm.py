import os
import re
import shutil

# Корневой каталог
ROOT_DIR = r"D:\Маммо_DBT\DBT_processing"

# Разрешённые номера итераций для каждого метода
ALLOWED_NUMBERS = {
    'MINRES': {'2', '4', '6', '8'},
    'MLEM':   {'5', '10', '15', '20', '25'},
    'SIRT':   {'5', '10', '15', '20', '25'}
}

# Регулярное выражение для извлечения метода и номера
# Ищем _МЕТОД_ЧИСЛО_slice (число может быть многозначным)
PATTERN = re.compile(r'_(MINRES|MLEM|SIRT)_(\d+)_slice')

def main():
    if not os.path.exists(ROOT_DIR):
        print(f"Ошибка: каталог {ROOT_DIR} не найден.")
        return

    for root, dirs, files in os.walk(ROOT_DIR):
        for filename in files:
            match = PATTERN.search(filename)
            if not match:
                continue  # файл не подходит

            method = match.group(1)
            number = match.group(2)

            # Определяем папку метода
            method_folder = os.path.join(root, method)

            # Проверяем, разрешён ли номер для данного метода
            if number in ALLOWED_NUMBERS.get(method, set()):
                # Создаём подпапку с номером
                target_folder = os.path.join(method_folder, number)
                os.makedirs(target_folder, exist_ok=True)
                # Перемещаем файл
                src_path = os.path.join(root, filename)
                dst_path = os.path.join(target_folder, filename)
                shutil.move(src_path, dst_path)
                print(f"Перемещён: {src_path} -> {dst_path}")
            else:
                # Если номер не в списке — перемещаем в корень папки метода (с предупреждением)
                # (можно также пропустить, но по условию таких файлов быть не должно)
                os.makedirs(method_folder, exist_ok=True)
                src_path = os.path.join(root, filename)
                dst_path = os.path.join(method_folder, filename)
                shutil.move(src_path, dst_path)
                print(f"Предупреждение: у файла {filename} номер {number} не разрешён для {method}. Перемещён в {method_folder}")

if __name__ == "__main__":
    main()