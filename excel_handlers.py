from typing import Generator
import ezodf
from pathlib import Path


def read_ods_and_xls_files(file_path: Path | str) -> list:
    """Чтение ods или xls файла"""
    doc = ezodf.opendoc(file_path)
    clean_rows = []
    for sheet in doc.sheets:
        cleared_row = []
        for row in sheet.rows():
            cleared_row.clear()
            for cell in row:
                try:
                    if cell.value is not None:
                        cleared_row.append(cell.value)
                except ValueError:
                    pass
            if cleared_row:
                clean_rows.append(cleared_row.copy())
    for index, row in enumerate(clean_rows):
        pass
        # print(index, row)
    return clean_rows


def read_ods_and_xls_dir(file_dir: Generator):
    """Чтение всей директории фалов с ods и xls"""
    layouts = []
    for index, file in enumerate(file_dir, start=1):
        if file.absolute().suffix.lower() not in (".xls", ".ods"):
            continue
        if "~" in str(file.absolute()):
            continue
        read_ods_and_xls_files(file)
        layouts.append(read_ods_and_xls_files(file))

    return layouts


def collect_data(data_list: list):
    """Обработка данных"""
    for layout in data_list:
        for row in layout:
            # if 'КИМ' in row:
            print(row)


if __name__ == "__main__":
    plasma_file_path = r"D:\АСУП\Python\Projects\PlasmaReport\misc\plasma_files"
    ods_file_path = r"D:\АСУП\Python\Projects\PlasmaReport\misc\ODS"
    xls_ods_files = Path(plasma_file_path).glob("*")
    # read_ods_and_xls_dir(xls_ods_files)
    one_file = (
        r"D:\АСУП\Python\Projects\PlasmaReport\misc\plasma_files\S245- 2-136661.ODS"
    )
    read_ods_and_xls_files(one_file)

    collect_data(read_ods_and_xls_dir(xls_ods_files))
