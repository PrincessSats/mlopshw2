# mlopshw2 — gRPC ML‑сервис для модели LogisticRegression (Iris)

Краткое описание
- Небольшой gRPC‑сервис на Python, который оборачивает заранее обученную модель (LogisticRegression на датасете Iris).
- Предоставляет сервис `PredictionService` с двумя методами:
    - `/health` (Health) — проверка работоспособности сервиса и версии модели.
    - `/predict` (Predict) — получение предсказания и оценки доверия (confidence).

## Структура репозитория

```
mlopshw2/
├── protos/
│   └── model.proto                 # gRPC-контракт (PredictionService, методы Health и Predict)
├── server/
│   ├── __init__.py
│   └── server.py                   # Реализация gRPC-сервера, загрузка модели, обработка запросов
├── client/
│   ├── __init__.py
│   └── client.py                   # Python-клиент для локального тестирования
├── models/
│   └── model.pkl                   # Обученная модель LogisticRegression (Iris)
├── model_pb2.py                    # Сгенерированные protobuf-сообщения
├── model_pb2_grpc.py               # Сгенерированный gRPC-stub
├── train_model.py                  # Скрипт обучения и сохранения модели
├── requirements.txt                # Python-зависимости
├── Dockerfile                      # Docker-образ для сервиса
├── .dockerignore                   # Исключения для сборки Docker
├── README.md                       # Документация проекта
└── docs/
    ├── screenshot1.png
    └── screenshot2.png
```



Сервис упакован в Docker и тестируется с помощью `grpcurl`.

Требования
- Docker
- grpcurl (для локального тестирования)

Быстрый старт

1. Сборка Docker‑образа

Из корня проекта выполните:

```bash
docker build -t grpc-ml-service .
```

Если требуется собрать для платформы linux/amd64 (Apple Silicon):

```bash
docker build --platform=linux/amd64 -t grpc-ml-service .
```

2. Запуск контейнера

```bash
docker run --rm -p 50051:50051 grpc-ml-service
```

Переопределение переменных окружения:

```bash
docker run --rm \
    -p 50051:50051 \
    -e MODEL_PATH=/app/models/model.pkl \
    -e MODEL_VERSION=v1.0.0 \
    grpc-ml-service
```

По умолчанию внутри контейнера установлены:
- PORT=50051
- MODEL_PATH=/app/models/model.pkl
- MODEL_VERSION=v1.0.0

После запуска gRPC‑сервер доступен по адресу: `localhost:50051`.

Примеры вызовов (grpcurl)
- Предполагается, что контейнер запущен и слушает порт 50051.

1) Эндпоинт /health

gRPC‑метод: `mlservice.v1.PredictionService/Health`

Команда:

```bash
grpcurl -plaintext localhost:50051 mlservice.v1.PredictionService/Health
```

Ожидаемый ответ (пример):

```json
{
    "status": "ok",
    "modelVersion": "v1.0.0"
}
```

2) Эндпоинт /predict

gRPC‑метод: `mlservice.v1.PredictionService/Predict`

Пример запроса (вектор признаков в формате Iris):

```bash
grpcurl -plaintext \
    -d '{"features":[5.1,3.5,1.4,0.2]}' \
    localhost:50051 \
    mlservice.v1.PredictionService/Predict
```

Пример ответа (структура):

```json
{
    "prediction": "0",
    "confidence": 0.97,
    "modelVersion": "v1.0.0"
}
```

Примечания
- Точные значения `prediction` и `confidence` зависят от обученной модели `model.pkl`.
- Для обновления модели замените файл по пути, указанному в `MODEL_PATH`, и перезапустите контейнер.
- Если необходима отладка внутри контейнера, можно добавить `-it` и команду `/bin/sh` при запуске.

Структура репозитория (пример)
- app/ — исходники сервиса
- models/model.pkl — обученная модель
- Dockerfile
- protos/ — файлы .proto

Контакты и поддержка
- Запросы по работе сервиса и баги — через систему issues в репозитории проекта.
