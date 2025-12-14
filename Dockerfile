FROM python:3.11-slim

ARG MODEL_VERSION_ARG=v1.0.0

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Значение версии по умолчанию
ENV MODEL_VERSION=v1.0.0
ENV MODEL_PATH=/app/models/model.pkl

# FastAPI через uvicorn, порт 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]