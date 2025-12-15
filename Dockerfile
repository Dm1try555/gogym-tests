FROM python:3.12-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов проекта
COPY . .

# Создание директории для результатов Allure
RUN mkdir -p allure-results

# По умолчанию запускаем все тесты
# Можно переопределить через docker-compose или docker run
CMD ["python", "run_all_tests.py"]