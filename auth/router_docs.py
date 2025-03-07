"""Документация endpoints сервиса auth."""

register_docs = {
    "response_description": "Результат регистрации пользователя",
    "summary": "Регистрация нового пользователя",
    "description": "Регистрация нового пользователя с проверкой уникальности email. Поле role необязательно и "
                   "по умолчанию присевается 'Пользователь'.",
    "responses":
        {
            200: {
                "description": "Пользователь успешно зарегистрирован",
                "content": {
                    "application/json": {
                        "example": {"message": "Вы успешно зарегистрированы!"},
                    },
                },
            },
            400: {
                "description": "Ошибка валидации или пользователь уже существует",
                "content": {
                    "application/json": {
                        "examples": {
                            "validation_error": {
                                "summary": "Ошибка валидации",
                                "value": {
                                    "detail": [
                                        {
                                            "loc": ["body", "email"],
                                            "msg": "Домен 'invalid.com' не разрешён",
                                            "type": "value_error",
                                        },
                                    ],
                                },
                            },
                            "user_exists": {
                                "summary": "Пользователь уже существует",
                                "value": {
                                    "detail": "Пользователь уже существует",
                                },
                            },
                        },
                    },
                },
            },
        },
}

login_docs = {
    "summary": "Аутентификация пользователя",
    "description": "Этот эндпоинт используется для входа пользователя в систему. Пользователь должен предоставить "
                   "действительную электронную почту (с разрешённым доменом) и пароль. После успешной аутентификации"
                   " создаются JWT-токены доступа и обновления, которые устанавливаются в HTTP-заголовки ответа.",
    "response_description": "Результат аутентификации пользователя",
    "responses": {
        401: {
            "description": "Неверная электронная почта или пароль",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"},
                },
            },
        },
        200: {
            "description": "Успешная аутентификация",
            "content": {
                "application/json": {
                    "example": {"ok": True, "message": "Авторизация успешна!"},
                },
            },
        },
    },
}

logout_docs = {
    "summary": "Выход пользователя",
    "description": "Этот эндпоинт используется для выхода пользователя из системы и удаления всех tokens.",
    "response_description": "Результат выхода пользователя из системы",
    "responses": {
        200: {
            "description": "Успешный выход из системы и удаление tokens",
            "content": {
                "application/json": {
                    "example": {"ok": True, "message": "Пользователь успешно вышел из системы."},
                },
            },
        },
    },
}

me_docs = {
    "summary": "Получение информации о текущем пользователе",
    "description": "Этот эндпоинт позволяет авторизованному пользователю получить информацию о себе, включая его имя, "
                   "фамилию, электронную почту и уникальный идентификатор.",
    "response_description": "Данные пользователя",
    "responses": {
        400: {
            "description": "Токен отсутствует в заголовке",
            "content": {
                "application/json": {
                    "example": {"detail": "Токен отсутствует в заголовке"},
                },
            },
        },
        200: {
            "description": "Успешное получение данных пользователя",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "user@example.com",
                        "role": "Пользователь",
                        "first_name": "Иван",
                        "last_name": "Иванов",
                    },
                },
            },
        },
    },
}
all_users_docs = {
    "summary": "Получение списка всех пользователей",
    "description": "Этот эндпоинт позволяет администратору получить список всех зарегистрированных пользователей "
                   "в системе. Только пользователи с ролью администратора имеют доступ к этому эндпоинту.",
    "response_description": "Список информации о пользователях",

    "responses": {

        400: {
            "description": "Токен отсутствует в заголовке",
            "content": {
                "application/json": {
                    "example": {"detail": "Токен отсутствует в заголовке"},
                },
            },
        },

        403: {
            "description": "Доступ запрещён (пользователь не является администратором)",
            "content": {
                "application/json": {
                    "example": {"detail": "Недостаточно прав"},
                },
            },
        },

        200: {
            "description": "Успешное получение списка пользователей",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "email": "admin@example.com",
                            "role": "Администратор",
                            "first_name": "Админ",
                            "last_name": "Иванов",
                        },
                        {
                            "id": 2,
                            "email": "user@example.com",
                            "role": "Пользователь",
                            "first_name": "Иван",
                            "last_name": "Петров",
                        },
                    ],
                },
            },
        },
    },
}

refresh_docs = {
    "summary": "Обновление access и refresh токенов",
    "description": "Этот эндпоинт используется для обновления пары JWT-токенов (access и refresh) "
                   "пользователя. Требуется валидный refresh-токен, передаваемый через cookies или заголовки.",
    "response_description": "Результат обновления токенов",
    "responses": {
        400: {
            "description": "Недействительный или отсутствующий refresh-токен",
            "content": {
                "application/json": {
                    "example": {"detail": "Токен отсутствует в заголовке"},
                },
            },
        },
        200: {
            "description": "Успешное обновление токенов",
            "content": {
                "application/json": {
                    "example": {"message": "Токены успешно обновлены"},
                },
            },
        },
    },
}
