---
title: PlasmaReport README
created: 05.06.2025
modified: 05.06.2025
---
# Установка 
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

- установить  `backendport` (если порт по умолчанию занят) в `/frontend/src/utils/urls.ts`
```typescript
export const BASE_URL = "http://localhost:some_port_numbers";
```

- Запуск предусмотрен только на windows (требования sigma-nest)
```text
start.bat из корня проекта
```

- установить миграции:
```
alembic revision --autogenerate
alembic upgrade head
```


## После запуска
- Администратору зарегистрировать пользователей. 
- Суперпользователю выдать роли пользователям через `server_ip:backend_port/admin`.
- Доступ к админке для изменения данных пользователей после регистрации:
    - `server_ip:backend_port/admin` - доступно только у суперпользователя. 
- регистрация пользователей через: `/auth/register` либо  через администратора `PlasmaReport`.
- доступ к swagger документации: `server_ip:backend_port/docs`

[[PlasmaReport]]
