import pyodbc
from config import settings


class Database:
    """
    Взаимодействие с БД MSSQL
    """

    def __init__(self):
        self.connection = None
        self.sigma_server = settings.sigma_server
        self.sigma_database = settings.sigma_database
        self.sigma_username = settings.sigma_username
        self.sigma_password = settings.sigma_password
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """Подключение к базе данных и создание курсора."""
        self.connection = pyodbc.connect('DRIVER=SQL Server;'
                                         'SERVER=' + self.sigma_server +
                                         ';DATABASE=' + self.sigma_database +
                                         ';UID=' + self.sigma_username +
                                         ';PWD=' + self.sigma_password)
        self.cursor = self.connection.cursor()

    def execute_query(self, query: str, params=()) -> None:
        """Выполнение запроса с поддержкой параметров."""
        self.cursor.execute(query, params)
        self.connection.commit()

    def get_columns(self):
        """Получение имён колонок"""
        return [column[0] for column in self.cursor.description]

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        """Получение всех данных из запроса."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query: str, params=()) -> list:
        """Получение одной записи из запроса."""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def close(self) -> None:
        """Закрытие соединения с базой данных."""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
