import os


def delete_raw_files_force():
    root_dir = r"D:\Маммо_DBT\DBT_processing"

    if not os.path.exists(root_dir):
        print(f"Ошибка: директория {root_dir} не найдена!")
        return

    deleted_count = 0
    error_count = 0

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.raw'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Удалён: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Ошибка при удалении {file_path}: {e}")
                    error_count += 1

    print(f"\nГотово! Удалено {deleted_count} файлов. Ошибок: {error_count}")


if __name__ == "__main__":
    delete_raw_files_force()