"""Работа с ODS файлами."""
import zipfile

from pathlib import Path

from logger_config import log


def extract_images_from_ods(ods_file_path: Path, output_dir: Path) -> None:
    """Получение картинки из ODS файла."""
    if not ods_file_path.exists():
        log.debug("Файл {ods_file_path} не найден.", od_file_path=ods_file_path)
        return

    try:
        # Открываем ODS как ZIP-архив
        with zipfile.ZipFile(ods_file_path, "r") as ods_zip:
            # Ищем все файлы с расширением, которое может быть изображением
            image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"]
            for file_name in ods_zip.namelist():
                # Проверяем, является ли файл изображением
                if any(file_name.lower().endswith(ext) for ext in image_extensions):
                    with output_dir.open("wb") as image_file:
                        image_file.write(ods_zip.read(file_name))
                    log.debug("Изображение извлечено: {extracted_path}", extracted_path=output_dir)
                    break
    except zipfile.BadZipFile as e:
        log.error("Ошибка: {ods_file_path} не является корректным ODS файлом.", ods_file_path=ods_file_path)
        log.exception(e)


if __name__ == "__main__":
    # ods_file_path = Path(r'D:\projects\PlasmaReport\misc\GS- 22-137856.ODS')  # Путь к вашему ODS файлу
    ods_file_path = Path(r"D:\projects\PlasmaReport\misc\GS- 22-137855.ODS")  # Путь к вашему ODS файлу
    output_dir = Path(r"D:\projects\PlasmaReport\misc\images")  # Директория для сохранения изображений
    extract_images_from_ods(ods_file_path, output_dir)
