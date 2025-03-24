"""Словарь переводчик полей БД sigma nest."""
translate_dict = {
    "ProgramName": "Имя программы",
    "RepeatIDProgram": "Повторов программы",
    "UsedArea": "Использованная площадь",
    # "ScrapFraction": "ScrapFraction",
    "MachineName": "Название машины",
    "CuttingTimeProgram": "Время резки программы",
    "PostDateTime": "Дата публикации",
    "Material": "Материал",
    "Thickness": "Толщина",
    "SheetLength": "Длина листа",
    "SheetWidth": "Ширина листа",
    # "ArchivePacketID": "ArchivePacketID",
    # "TimeLineID": "TimeLineID",
    "Comment": "Комментарий",
    "PostedByUserID": "Опубликовано пользователем",
    "PierceQtyProgram": "Количество врезок",
    "UserName": "Полное имя пользователя",
    "UserFirstName": "Имя пользователя",
    "UserLastName": "Фамилия пользователя",
    "UserEmail": "Email пользователя",
    "LastLoginDate": "Дата последнего входа",
    "path_to_ods": "Путь к файлу ODS",
    # "master_fio_id": "master_fio_id",
    "time_program_started": "Время начала программы",
    "time_program_finished": "Время окончания программы",
    "program_status": "Статус программы",
    "program_priority": "Приоритет программы",
    "created_at": "Дата создания",
    "updated_at": "Дата обновления",
    "WONumber": "Номер заказа",
    "CustomerName": "Название заказчика",
    "WODate": "Дата подряда",
    "OrderDate": "Дата заказа",
    "WOData1": "Дополнительная информация1",
    "WOData2": "Дополнительная информация2",
    "DateCreated": "Дата создания заказа",
    "wo_status": "Статус заказа",
    # "wo_number_id": "wo_number_id",
    # "program_id": "program_id",
    "storage_cell_id": "Ячейка хранения",
    "done_by_fio_doer_id": "done_by_fio_doer_id",
    "PartName": "Деталь",
    "QtyInProcess": "Деталей в процесса",
    "PartLength": "Длина детали",
    "PartWidth": "Ширина детали",
    "TrueArea": "Истинная площадь",
    "RectArea": "Площадь Rect",
    "TrueWeight": "Истинный вес",
    "RectWeight": "Вес Rect",
    "CuttingTimePart": "Время резки детали",
    "CuttingLength": "Длина резки",
    "PierceQtyPart": "Количество врезок детали",
    "NestedArea": "Площадь Nested",
    "TotalCuttingTime": "Общее время резки",
    # "MasterPartQty": "MasterPartQty",
    # "WOState": "WOState",
    "DueDate": "Дата окончания",
    "RevisionNumber": "Номер ревизии",
    # "PK_PIP": "PK_PIP",
    "part_status": "Статус детали",
    "qty_fact": "Фактическое количество",
    "SourceFileName": "dxf файл",
    "fio_doers": "Исполнители",
    "Cuttingtime": "Время реза",
    "NetArea": "Площадь Net",
    "Netweight": "Вес Net",
    "QtyOrdered": "Количество заказано",
    "QtyCompleted": "Количество выполнено",
    "QtyRemaining": "Количество осталось",
}


def translate_keys(list_of_dicts_to_translate: list) -> list:
    """Функция для перевода ключей в списках словарей."""
    translated_list = []

    for dictionary in list_of_dicts_to_translate:
        # Создаем новый словарь с переведёнными ключами
        translated_dict = {
            translate_dict.get(key, key): value  # Если ключа нет в словаре перевода, оставляем его без изменений
            for key, value in dictionary.items()
        }
        # Добавляем переведённый словарь в результирующий список
        translated_list.append(translated_dict)

    return translated_list


def get_translated_keys(input_list: list) -> dict:
    """Получение переведённых ключей из списка словарей."""
    input_dict = input_list[0]
    return {key: translate_dict[key] for key, value in input_dict.items() if key in translate_dict}
