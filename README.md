# CutIt

Сервис для сокращения длинных ссылок

# 1. Установка зависимостей

pip install -r requirements.txt

# 2. Запуск docker-compose

docker-compose up -d

# 3. Создайте .env следующего вида

DB_USER=user
DB_PASS=pass
DB_HOST=host
DB_PORT=5432
DB_NAME=name

SECRET_KEY=key

CLEANUP_DAYS=60

# 4. Запуск приложения

python -m uvicorn src.main:app --reload

Документация Swagger: http://localhost:8000/docs

# Пример запроса

curl -X POST "http://localhost:8000/api/links/shorten?original_url=google.com&custom_alias=pupsen"