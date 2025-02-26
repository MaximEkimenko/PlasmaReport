"""Работа с ODS файлами."""
import zipfile

from pathlib import Path


def extract_images_from_ods(ods_file_path: Path, output_dir: Path) -> None:
    """Получение картинки из ODS файла."""
    # Проверяем, существует ли файл ODS
    if not ods_file_path.exists():
        print(f"Файл {ods_file_path} не найден.") # noqa
        return

    # Создаем директорию для извлеченных изображений, если её нет
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Открываем ODS как ZIP-архив
        with zipfile.ZipFile(ods_file_path, "r") as ods_zip:
            # Ищем все файлы с расширением, которое может быть изображением
            image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"]
            for file_name in ods_zip.namelist():
                # Проверяем, является ли файл изображением
                if any(file_name.lower().endswith(ext) for ext in image_extensions):
                    # Извлекаем файл в указанную директорию
                    extracted_path = output_dir / Path(file_name).name
                    with extracted_path.open("wb") as image_file:
                        image_file.write(ods_zip.read(file_name))
                    print(f"Изображение успешно извлечено: {extracted_path}") # noqa
    except zipfile.BadZipFile:
        print(f"Ошибка: {ods_file_path} не является корректным ODS файлом.") # noqa



# Пример использования

if __name__ == "__main__":
    # ods_file_path = Path(r'D:\projects\PlasmaReport\misc\GS- 22-137856.ODS')  # Путь к вашему ODS файлу
    ods_file_path = Path(r"D:\projects\PlasmaReport\misc\GS- 22-137851.ODS")  # Путь к вашему ODS файлу
    output_dir = Path(r"D:\projects\PlasmaReport\misc\images")  # Директория для сохранения изображений
    extract_images_from_ods(ods_file_path, output_dir)

