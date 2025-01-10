from pprint import pprint
from sigma_handlers.database import Database


def get_sigma_data():
    """
    Получение данных из базы sigma nest
    """
    # запрос
    query = f"""
        SELECT WONumber, PartName, Cuttingtime, QtyCompleted
        FROM dbo.PartWithQtyInProcess
        """
    #     WHERE ProgramName = 'SP RIFL- 4-135871'
    with Database() as db:
        result = db.fetch_all(query)
        columns = db.get_columns()
        results = [dict(zip(columns, row)) for row in result]

    pprint(results)

    # TODO requests examples
    # for row in cursor.execute("select user_id, user_name from users"):
    #     print(row.user_id, row.user_name)

    # cursor.execute("""
    #     select user_id, user_name
    #       from users
    #      where last_logon < ?
    #        and bill_overdue = ?
    # """, [datetime.date(2001, 1, 1), 'y'])
    # inserting
    # cursor.execute("insert into products(id, name) values (?, ?)", 'pyodbc', 'awesome library')
    # cnxn.commit()

    # TODO sigma db credentials
    # 'sigma': {
    #     'NAME': 'SNDBase',
    #     'ENGINE': 'mssql',
    #     'USER': 'SNUser',
    #     'PASSWORD': 'BestNest1445',
    #     'HOST': r'APM-0230\SIGMANEST',
    #     # "OPTIONS": {"driver": "ODBC Driver 17 for SQL Server"}
    # },


if __name__ == '__main__':
    get_sigma_data()
