from settings.translate_dict import translate_dict
from sigma_handlers.sigma_db import get_sigma_data
import datetime

# TODO
#  словарь переводчик-сортировщик полей таблицы на человеческий доступный для пользователя
#  результирующий отсортированный список словарей из БД
#  создания xlsx по результирующему словарю
#  ручки FastAPI на получение xlsx с выбором даты
#  аутентификация авторизация средствами FastAPI
#  словарь настроек форматирования xlsx
#  UI FRONT? Попробовать сделать простой на VUE.js 3
#  cmd (bash) script по развёртке на приложения на клиенте
#  запуск с ярлыка на 0.0.0.0 (совместно с FRONT?) лучше запускать на том же сервере, что и sigma
#  раздача ссылок заинтересованным

def main():
    """Точка входа в приложение"""
    start_date = datetime.date(2025, 1, 1)  # дата начала выборки
    end_date = datetime.date(2025, 1, 10)  # дата окончания выборки
    sigma_data = get_sigma_data(start_date=start_date, end_date=end_date)
    print(sigma_data)
    # translated_data = [translate_dict(record) for record in sigma_data]



if __name__ == "__main__":
    main()

