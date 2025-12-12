# Лабораторна робота 4 - Система обліку витрат з JWT аутентифікацією

## Опис

Розширений Flask додаток для обліку витрат та доходів з повноцінною JWT
аутентифікацією. Додаток реалізує систему управління фінансами з
категоріями витрат, рахунками користувачів та автоматичною перевіркою
балансу.

## Виконавець

**Бондар Ярослав ІМ-33**

**Варіант: 3 - Облік доходів з JWT аутентифікацією**

## Технологічний стек

-   Python 3.11
-   Flask 2.3.3
-   Flask-JWT-Extended 4.6.0
-   Flask-SQLAlchemy 3.0.5
-   Flask-Migrate 4.0.5
-   PostgreSQL 15
-   Gunicorn
-   Docker & Docker Compose
-   Render.com
-   Swagger/OpenAPI 3.0

## Архітектура проєкту

    expense-tracker/
    ├── app/
    │   ├── models/
    │   │   ├── user.py
    │   │   ├── account.py
    │   │   ├── category.py
    │   │   ├── expense.py
    │   │   └── income.py
    │   ├── routes/
    │   │   ├── auth_routes.py
    │   │   ├── user_routes.py
    │   │   ├── account_routes.py
    │   │   ├── category_routes.py
    │   │   └── expense_routes.py
    │   ├── schemas/
    │   └── __init__.py
    ├── tests/
    ├── docker-compose.yml
    ├── Dockerfile
    ├── requirements.txt
    ├── render.yaml
    └── README.md

## Реалізована аутентифікація

-   JWT
-   Реєстрація з валідацією
-   Логін з видачею токенів
-   Оновлення access токена
-   PBKDF2 хешування

## Моделі даних

### User

-   id
-   name
-   email
-   password_hash
-   created_at

### Account

-   id
-   user_id
-   balance
-   timestamps

### Category

-   id
-   name
-   is_global
-   user_id

### Expense

-   id
-   user_id
-   category_id
-   account_id
-   amount
-   description

### Income

-   id
-   account_id
-   amount
-   description

## API Ендпоінти

### Публічні:

#### GET /

Повертає інформацію про API.

#### GET /healthcheck

Перевірка стану сервісу.

#### GET /swagger-ui

Документація API.

### Аутентифікація

#### POST /api/auth/register

Реєстрація користувача.

#### POST /api/auth/login

Отримання JWT токенів.

#### POST /api/auth/refresh

Оновлення токена.

#### GET /api/auth/me

Поточний користувач.

### Користувачі

CRUD та статистика.

### Рахунки

CRUD, перегляд балансу, додавання доходів.

### Категорії

CRUD, глобальні та персональні категорії.

### Витрати

CRUD та статистика.

## Локальний запуск

### Docker Compose

    git clone <repository-url>
    cd expense-tracker
    docker-compose up --build

### Без Docker

Створення середовища, встановлення залежностей, міграції, запуск
сервера.

## Деплой на Render.com

Підготовка репозиторію, налаштування середовищ, запуск Gunicorn.

## Тестування API

Postman або curl.

## Автоматичні тести

    pytest tests/
    pytest --cov=app tests/

## Демо

https://flask-healthcheck-app.onrender.com

## Вимоги

-   Python 3.11+
-   PostgreSQL 12+
-   512MB RAM
-   1GB диску

## Ліцензія

Проєкт створено для навчальних цілей.

## Контакти

Бондар Ярослав, ІМ-33 Дисципліна: Технології серверного програмного
забезпечення
