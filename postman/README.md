1. Healthcheck & Info

    GET /healthcheck - Перевірка стану сервера

    GET / - Інформація про API

    GET /swagger-ui - Інтерактивна документація Swagger

2. Authentication

    POST /api/auth/register - Реєстрація нового користувача

    POST /api/auth/login - Вхід та отримання JWT токенів

    POST /api/auth/refresh - Оновлення access токена

    GET /api/auth/me - Профіль поточного користувача

    POST /api/auth/logout - Вихід з системи

3. Users

    GET /api/users - Список користувачів

    GET /api/users/{id} - Отримання користувача за ID

    PUT /api/users/{id} - Оновлення користувача

    DELETE /api/users/{id} - Видалення користувача

    GET /api/users/{id}/stats - Статистика користувача

4. Accounts

    GET /api/accounts - Список рахунків

    POST /api/accounts - Створення рахунку

    GET /api/accounts/{id} - Отримання рахунку

    DELETE /api/accounts/{id} - Видалення рахунку

    GET /api/accounts/{id}/balance - Баланс рахунку

5. Income Management

    POST /api/accounts/{id}/income - Додавання доходу

    GET /api/accounts/{id}/income - Історія доходів

    GET /api/accounts/{id}/income?start_date=...&end_date=... - Фільтрація за датами

6. Categories

    GET /api/categories - Всі категорії

    GET /api/categories/global - Тільки глобальні категорії

    POST /api/categories - Створення категорії

    PUT /api/categories/{id} - Оновлення категорії

    DELETE /api/categories/{id} - Видалення категорії

Типи категорій:

    Глобальні (is_global: true) - доступні всім

    Персональні (is_global: false) - тільки для власника

7. Expenses (Оновлено - вимагає авторизації)

    GET /api/expenses - Список витрат

    GET /api/expenses/summary - Статистика витрат

    POST /api/expenses - Створення витрати

    GET /api/expenses/{id} - Отримання витрати

    PUT /api/expenses/{id} - Оновлення витрати

    DELETE /api/expenses/{id} - Видалення витрати
