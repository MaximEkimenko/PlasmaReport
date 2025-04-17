"""Тесты для copy_pics_and_get_links.py."""
# ruff: noqa: TRY002, ARG001
from pathlib import Path

import pytest

from _pytest.monkeypatch import MonkeyPatch

from utils.pics_utils.copy_pics_and_get_links import get_part_image, get_program_image

# Настройка pytest для асинхронных тестов
pytestmark: pytest.MarkDecorator = pytest.mark.asyncio(loop_scope="session")


# Фикстуры для путей
@pytest.fixture
def mock_config_paths(tmp_path: Path) -> dict[str, Path]:
    """Создает временные пути для PARTS_DIR, REPORTS_DIR, STATIC_IMAGES_DIR."""
    parts_dir: Path = tmp_path / "parts"
    reports_dir: Path = tmp_path / "reports"
    static_images_dir: Path = tmp_path / "static/images"

    parts_dir.mkdir(parents=True)
    reports_dir.mkdir(parents=True)
    static_images_dir.mkdir(parents=True)

    return {
        "PARTS_DIR": parts_dir,
        "REPORTS_DIR": reports_dir,
        "STATIC_IMAGES_DIR": static_images_dir,
    }


# Фикстура для мокирования config
@pytest.fixture
def mock_config(mock_config_paths: dict[str, Path], monkeypatch: MonkeyPatch) -> None:
    """Мокирует пути в config."""
    monkeypatch.setattr("utils.pics_utils.copy_pics_and_get_links.PARTS_DIR", mock_config_paths["PARTS_DIR"])
    monkeypatch.setattr("utils.pics_utils.copy_pics_and_get_links.REPORTS_DIR", mock_config_paths["REPORTS_DIR"])
    monkeypatch.setattr("utils.pics_utils.copy_pics_and_get_links.STATIC_IMAGES_DIR",
                        mock_config_paths["STATIC_IMAGES_DIR"])


# Тесты для get_part_image
async def test_get_part_image_success(mock_config: None, mock_config_paths: dict[str, Path]) -> None:
    """Тестирует успешное копирование BMP-файла."""
    part_name: str = "test_part"
    source_path: Path = mock_config_paths["PARTS_DIR"] / f"{part_name}.bmp"
    dest_path: Path = mock_config_paths["STATIC_IMAGES_DIR"] / f"{part_name}.bmp"

    # Создаем пустой исходный файл
    source_path.touch()

    result: str | None = await get_part_image(part_name)

    assert result == f"/static/images/{part_name}.bmp"
    assert dest_path.exists()


async def test_get_part_image_already_exists(mock_config: None, mock_config_paths: dict[str, Path]) -> None:
    """Тестирует возврат URL, если BMP уже существует."""
    part_name: str = "test_part"
    dest_path: Path = mock_config_paths["STATIC_IMAGES_DIR"] / f"{part_name}.bmp"

    dest_path.touch()

    result: str | None = await get_part_image(part_name)

    assert result == f"/static/images/{part_name}.bmp"


async def test_get_part_image_source_not_found(mock_config: None, mock_config_paths: dict[str, Path]) -> None:
    """Тестирует случай, когда исходный BMP не существует."""
    part_name: str = "test_part"

    result: str | None = await get_part_image(part_name)

    assert result is None


async def test_get_part_image_copy_error(mock_config: None, mock_config_paths: dict[str, Path],
                                         monkeypatch: MonkeyPatch) -> None:
    """Тестирует ошибку при копировании BMP."""
    part_name: str = "test_part"
    source_path: Path = mock_config_paths["PARTS_DIR"] / f"{part_name}.bmp"

    source_path.touch()

    # Мокируем shutil.copy2 для имитации ошибки
    def raise_error() -> None:
        msg = "Copy error"
        raise Exception(msg)

    monkeypatch.setattr("shutil.copy2", raise_error)

    result: str | None = await get_part_image(part_name)

    assert result is None


# Тесты для get_program_image
async def test_get_program_image_success(mock_config: None, mock_config_paths: dict[str, Path],
                                         monkeypatch: MonkeyPatch) -> None:
    """Тестирует успешное извлечение PNG из ODS."""
    program_name: str = "test_program"
    ods_path: Path = mock_config_paths["REPORTS_DIR"] / f"{program_name}.ods"
    dest_path: Path = mock_config_paths["STATIC_IMAGES_DIR"] / f"{program_name}.png"

    ods_path.touch()

    # Мокируем extract_images_from_ods для создания файла
    def mock_extract_images_from_ods(ods_path: str | Path, dest_path: str | Path) -> None:
        Path(dest_path).touch()

    monkeypatch.setattr("utils.pics_utils.copy_pics_and_get_links.extract_images_from_ods",
                        mock_extract_images_from_ods)

    result: str | None = await get_program_image(program_name)

    assert result == f"/static/images/{program_name}.png"
    assert dest_path.exists()


async def test_get_program_image_already_exists(mock_config: None, mock_config_paths: dict[str, Path]) -> None:
    """Тестирует возврат URL, если PNG уже существует."""
    program_name: str = "test_program"
    dest_path: Path = mock_config_paths["STATIC_IMAGES_DIR"] / f"{program_name}.png"

    dest_path.touch()

    result: str | None = await get_program_image(program_name)

    assert result == f"/static/images/{program_name}.png"


async def test_get_program_image_ods_not_found(mock_config: None, mock_config_paths: dict[str, Path]) -> None:
    """Тестирует случай, когда ODS-файл не существует."""
    program_name: str = "test_program"

    result: str | None = await get_program_image(program_name)

    assert result is None


async def test_get_program_image_extract_error(mock_config: None, mock_config_paths: dict[str, Path],
                                               monkeypatch: MonkeyPatch) -> None:
    """Тестирует ошибку при извлечении PNG."""
    program_name: str = "test_program"
    ods_path: Path = mock_config_paths["REPORTS_DIR"] / f"{program_name}.ods"

    ods_path.touch()

    # Мокируем extract_images_from_ods для имитации ошибки
    def raise_error() -> None:
        msg = "Extract error"
        raise Exception(msg)

    monkeypatch.setattr("utils.pics_utils.copy_pics_and_get_links.extract_images_from_ods", raise_error)

    result: str | None = await get_program_image(program_name)

    assert result is None
