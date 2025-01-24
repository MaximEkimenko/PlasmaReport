from settings.translate_dict import translate_dict
from plasma_exceptions import WrongTranslateSettingsError
import datetime


def create_sorted_named_cols(column_names: tuple, results: list) -> list:
    """Получение отсортированного переименованного словаря"""
    if len(column_names) != len(translate_dict):
        raise WrongTranslateSettingsError(
            f"Несовпадения словаря настроек с БД - "
            f"длина БД:{len(column_names)}, "
            f"длина настроек {len(translate_dict)}"
        )

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
        raise WrongTranslateSettingsError(
            f"В словаре настроек translate_dict неверно заполнено: {e.args[0]}."
        )

    return sorted_results


if __name__ == "__main__":
    pass
    a = datetime.datetime.timestamp(datetime.datetime.now())
    print(a)
