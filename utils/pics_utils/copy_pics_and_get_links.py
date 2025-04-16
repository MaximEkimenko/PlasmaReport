"""Модуль для копирования картинок программ и деталей в static/images."""
import shutil
import asyncio

from config import PARTS_DIR, REPORTS_DIR, STATIC_IMAGES_DIR
from logger_config import log
from utils.pics_utils.program_ods_to_png import extract_images_from_ods


# Асинхронная функция для копирования картинки детали
async def get_part_image(part_name: str) -> str | None:
    """Асинхронно копирует BMP-файл детали в static/images и возвращает URL.

    Если файл уже существует или исходный файл не найден, копирование пропускается.
    """
    source_path = PARTS_DIR / f"{part_name}.bmp"
    dest_path = STATIC_IMAGES_DIR / f"{part_name}.bmp"
    image_url = f"/static/images/{part_name}.bmp"

    if dest_path.exists():
        log.debug("{part_name} image already exists in static/images", part_name=part_name)
        return image_url

    if source_path.exists():
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, shutil.copy2, source_path, dest_path)
        except Exception as e:
            log.error("Error copying {part_name}", part_name=part_name)
            log.exception(e)
            return None
        else:
            log.debug("Copied {part_name} image to static/images from sigma server", part_name=part_name)
            return image_url

    return None


# Асинхронная функция для извлечения и копирования картинки программы
async def get_program_image(program_name: str) -> str | None:
    """Асинхронно извлекает PNG из ODS, сохраняет как program_name.png в static/images и возвращает URL.

    Если файл уже существует или ODS не найден, копирование пропускается.
    """
    ods_path = REPORTS_DIR / f"{program_name}.ods"
    dest_path = STATIC_IMAGES_DIR / f"{program_name}.png"
    image_url = f"/static/images/{program_name}.png"

    if dest_path.exists():
        log.debug("{program_name} image already exists in static/images", program_name=program_name)
        return image_url

    if ods_path.exists():
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, extract_images_from_ods, ods_path, dest_path)
        except Exception as e:
            log.error("Error extracting {program_name}", program_name=program_name)
            log.exception(e)
            return None
        else:
            log.debug("Extracted {program_name} image from ODS to static/images", program_name=program_name)
            return image_url

    return None
