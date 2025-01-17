from sigma_handlers.sigma_db import get_column_names
from settings.translate_dict import translate_dict
from plasma_exceptions import WrongTranslateSettingsError


def create_sorted_named_dict(translate_dict: dict, column_names: tuple) -> dict:
    """Получение отсортированного именованного словаря"""

    if len(column_names) != len(translate_dict):
        raise WrongTranslateSettingsError(f"Неверное заполнение словаря настроек "
                                          f"длина БД:{len(column_names)}, "
                                          f"длина настроек {len(translate_dict)}")

    try:
        # для случае если можно пропускать поля с ошибками
        # result_dict = {col: translate_dict.get(col, None) for col in column_names}
        result_dict = {col: translate_dict[col] for col in column_names}
    except KeyError as e:
        raise WrongTranslateSettingsError(f"Неверно заполнено: {e.args[0]}. В словаре настроек.")

    return result_dict


if __name__ == '__main__':
    columns, _ = get_column_names()

    print(create_sorted_named_dict(translate_dict=translate_dict,
                                   column_names=columns))
