---
title: PlasmaReport README
created: 05.06.2025
modified: 05.06.2025
---
# Установка (только windows) 
- Клонировать проект:
```bash
git clone <project link>
```

- Скопировать на сервер (заполнить самостоятельно ) `.env` файл с переменными окружения, например:
```text
DB_NAME="plasma_report.db"
SIGMA_SERVER="APM-SIGMA\SIGMANEST"
SIGMA_DATABASE='SigamDataBaseNanme'
SIGMA_USERNAME='SigmaUserName'
SIGMA_PASSWORD='SigmaPassword'
SECRET_KEY=VerySecrtKey
ALGORITHM="HS256"
SUPER_USER_PASSWORD="SuperUserPassword"
SUPER_USER="SuperUserName"
```

- Установить uv на сервер.
```bash
pip install uv
```

- Установить виртуальное окружение с зависимостями:
```bash
uv sync
```

- установить npm [скачать](https://nodejs.org/en?spm=a2ty_o01.29997173.0.0.2142c921xbsYJI) без лишних зависимостей. 
- установить зависимости frontend
```bash
npm i 
#или 
npm install 
```

- установить  `ip:port` в `/frontend/src/utils/urls.ts`
```typescript
export const BASE_URL = "http://localhost:some_port_numbers";
```

- Добавить `ip:port` серверов в список `origins`  файла `main.py`
```python
origins = [
...
    "192.168.8.144:5173",
    "192.168.8.144:8010",
...
]
```

- установить миграции:
```
alembic revision --autogenerate
alembic upgrade head
```

- Запуск предусмотрен только на windows (требования sigma-nest)
```text
start.bat из корня проекта
```

## После запуска
- Администратору зарегистрировать пользователей. 
- Суперпользователю выдать роли пользователям через `server_ip:backend_port/admin`.
- Доступ к админке для изменения данных пользователей после регистрации:
    - `server_ip:backend_port/admin` - доступно только у суперпользователя. 
- регистрация пользователей через: `/auth/register` либо  через администратора `PlasmaReport`.
- доступ к swagger документации: `server_ip:backend_port/docs`

[[PlasmaReport]]
