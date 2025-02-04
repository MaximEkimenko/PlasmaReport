"""Утилиты общего назначения всего приложения."""

from exceptions import WrongTranslateSettingsError
from settings.translate_dict import translate_dict


def create_sorted_named_cols(column_names: tuple, results: list) -> list:
    """Получение отсортированного переименованного словаря."""
    if len(column_names) != len(translate_dict):
        raise WrongTranslateSettingsError(column_names=column_names, translate_dict=translate_dict)

    try:
        sorting_keys = list(translate_dict.keys())  # список по которому сортировка
        sorted_results = [
            {
                translate_dict[
                    key
                ]: val  # Переименовываем ключи согласно translate_dict
                for key, val in sorted(
                    result.items(),  # Сортируем пары "ключ-значение" из словаря
                    key=lambda x: sorting_keys.index(x[0])  # Определяем порядок ключей
                    # Если ключа нет в translate_dict, ставим его в конец
                    if x[0] in sorting_keys
                    else len(sorting_keys),
                )
            }
            for result in results  # Применяем операцию ко всем словарям в списке results
        ]
    except KeyError as e:
        raise WrongTranslateSettingsError(error_args=e.args[0]) from e
    else:
        return sorted_results
