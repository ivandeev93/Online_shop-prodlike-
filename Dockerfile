FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Создаём непривилегированного пользователя
RUN groupadd --system app \
    && useradd --system --gid app app \
    && mkdir -p /app/media/products \
    && chown -R app:app /app

# Сначала копируем зависимости для эффективного кеширования Docker
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируем приложение и конфигурацию миграций
COPY --chown=app:app app ./app
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app alembic.ini .

# Запускаем приложение не от root
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
