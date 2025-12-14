# mlopshw2 — Автоматизированное развертывание ML‑сервиса (FastAPI, CI/CD, Blue‑Green)

Минимальный ML‑сервис на FastAPI, оборачивающий предобученную модель LogisticRegression по Iris. Две версии сервиса (v1.0.0 и v1.1.0) разворачиваются стратегией Blue‑Green через docker-compose; сборка и публикация образов автоматизированы GitHub Actions.

## Содержание
- [Кратко о сервисе](#кратко-о-сервисе)
- [Структура репозитория](#структура-репозитория)
- [Локальная сборка и запуск (Docker)](#локальная-сборка-и-запуск-docker)
- [HTTP API](#http-api)
- [Blue-Green deployment](#blue-green-deployment)
- [CI/CD (GitHub Actions)](#cicd-github-actions)
- [Переменные окружения](#переменные-окружения)
- [Скриншоты](#скриншоты)
- [gRPC-код из модуля 2](#grpc-код-из-модуля-2)

## Кратко о сервисе
- REST API на FastAPI: `GET /health`, `POST /predict`.
- Модель: логистическая регрессия по датасету Iris (`models/model.pkl`).
- Версия модели прокидывается через `MODEL_VERSION` (возвращается в `/health` и `/predict`).
- Контейнеризация в Docker, запуск на порту `8080`.
- Две версии сервиса с Blue‑Green переключением через отдельные `docker-compose.*.yml`.

## Структура репозитория
```text
mlopshw2/
  app/
    __init__.py
    main.py                 # REST API (FastAPI): /health и /predict
  models/
    model.pkl               # заранее обученная ML-модель
  protos/
    model.proto             # gRPC-контракт (для совместимости с модулем 2)
  server/
    server.py               # gRPC-сервер (из модуля 2)
  client/
    client.py               # gRPC-клиент (локальное тестирование)
  model_pb2.py
  model_pb2_grpc.py
  train_model.py            # скрипт обучения и сохранения model.pkl
  requirements.txt          # Python-зависимости
  Dockerfile                # образ REST-сервиса
  docker-compose.blue.yml   # Blue-версия (v1.0.0)
  docker-compose.green.yml  # Green-версия (v1.1.0)
  .github/
    workflows/
      deploy.yml            # CI/CD-pipeline (GitHub Actions)
  docs/
    health_green.png
    predict_green.png
  README.md                 # текущий файл
```

## Локальная сборка и запуск (Docker)
1) Сборка образа:
```bash
docker build -t ml-service:v1.0.0 --build-arg MODEL_VERSION_ARG=v1.0.0 .
# для новой версии:
docker build -t ml-service:v1.1.0 --build-arg MODEL_VERSION_ARG=v1.1.0 .
```
2) Запуск одной версии:
```bash
docker run --rm -p 8080:8080 ml-service:v1.0.0
```
По умолчанию в контейнере:
- `MODEL_PATH=/app/models/model.pkl`
- `MODEL_VERSION` — из `MODEL_VERSION_ARG` при сборке или переопределите через `-e MODEL_VERSION=...`.

## HTTP API
- `GET /health` — проверка состояния и версии.
  ```bash
  curl http://localhost:8080/health
  ```
  Пример ответа:
  ```json
  { "status": "ok", "version": "v1.0.0" }
  ```
- `POST /predict` — инференс.
  ```bash
  curl -X POST http://localhost:8080/predict \
    -H "Content-Type: application/json" \
    -d '{"features":[5.1,3.5,1.4,0.2]}'
  ```
  Пример ответа:
  ```json
  {
    "prediction": "0",
    "confidence": 0.97,
    "version": "v1.0.0"
  }
  ```
  Точные значения `prediction` и `confidence` зависят от модели `model.pkl`.

## Blue-Green deployment
В репозитории две docker-compose конфигурации. Оба сервиса поднимают HTTP на `8080:8080`.

- **Blue (v1.0.0)** — `docker-compose.blue.yml`
  ```bash
  docker compose -f docker-compose.blue.yml up -d
  curl http://localhost:8080/health  # → version: "v1.0.0"
  ```

- **Green (v1.1.0)** — `docker-compose.green.yml`
  ```bash
  docker compose -f docker-compose.blue.yml down     # остановить старую версию
  docker compose -f docker-compose.green.yml up -d   # запустить новую
  curl http://localhost:8080/health  # → version: "v1.1.0"
  ```

Откат:
```bash
docker compose -f docker-compose.green.yml down
docker compose -f docker-compose.blue.yml up -d
curl http://localhost:8080/health  # убедиться, что снова v1.0.0
```

## CI/CD (GitHub Actions)
Workflow: `.github/workflows/deploy.yml`.
- Триггер: `push` в `main`.
- Шаги: checkout → сборка Docker-образа `ghcr.io/<owner>/<repo>:<sha>` с версией модели из `secrets.MODEL_VERSION` → логин в GHCR → push образа → HTTP-вызов внешнего API деплоя.
- Пример деплоя внутри workflow:
  ```bash
  curl -X POST https://api.cloudprovider/deploy \
    -H "Authorization: Bearer ${{ secrets.CLOUD_TOKEN }}" \
    -H "Content-Type: application/json" \
    -d "{\"image\":\"ghcr.io/${{ github.repository }}:${{ github.sha }}\",\"version\":\"${{ secrets.MODEL_VERSION }}\"}"
  ```
- Секреты в Settings → Secrets → Actions:
  - `CLOUD_TOKEN` — токен для API деплоя.
  - `MODEL_VERSION` — актуальная версия модели (например, `v1.0.0` или `v1.1.0`).

<<<<<<< HEAD
=======
## Переменные окружения
| Переменная       | Назначение                                | Значение по умолчанию            |
|------------------|-------------------------------------------|----------------------------------|
| `MODEL_PATH`     | Путь к файлу модели                       | `/app/models/model.pkl`          |
| `MODEL_VERSION`  | Версия модели, отдаётся в ответах         | `v1.0.0`                         |
| `PORT`           | Порт gRPC-сервера (`server/server.py`)    | `50051`                          |

## Скриншоты
Снимки после деплоя (`docs/`): `health_green.png`, `predict_green.png` (и др.).

## gRPC-код из модуля 2
В репозитории сохранён gRPC-сервис из предыдущего модуля (`protos/`, `server/server.py`, `client/client.py`, `model_pb2*.py`). Он не используется в Blue‑Green и CI/CD потоке модуля 3, но остаётся для совместимости и локальных тестов.
>>>>>>> e51cee8 (All for HW3)
