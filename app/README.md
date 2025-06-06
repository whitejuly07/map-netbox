# Network Topology Backend (FastAPI)

Бэкенд-приложение для визуализации и синхронизации сетевой топологии. Построен на **FastAPI** и использует **SQLAlchemy** с SQLite, а также взаимодействует с NetBox для получения информации об устройствах и подключениях.

## 📦 Стек технологий

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](https://www.sqlite.org/)
- [httpx](https://www.python-httpx.org/) — HTTP-клиент
- [NetBox](https://netbox.dev/) — внешний источник данных
- WebSocket — синхронизация карты в реальном времени

## 📁 Структура проекта

```
backend/
├── main.py            # Точка входа FastAPI
├── models.py          # SQLAlchemy-модели
├── crud.py            # CRUD-операции
├── database.py        # Подключение к базе данных
├── netbox_client.py   # Асинхронный клиент для NetBox
└── config.py          # Настройки (токен, URL NetBox)
```

## 🚀 Установка и запуск

### 1. Установка зависимостей

Рекомендуется использовать виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Запуск приложения

```bash
uvicorn main:app --reload
```

По умолчанию сервер будет доступен на `http://localhost:8000`.

## 🔌 Основные эндпоинты API

- `GET /api/devices` — получить список устройств
- `GET /api/topology` — получить соединения (кабели и порты)
- `GET /api/positions` — получить координаты устройств
- `POST /api/positions` — сохранить координаты устройств
- `POST /api/update` — загрузить данные из NetBox
- `WebSocket /ws` — канал для обновлений карты в реальном времени

## ⚙️ Конфигурация

Создайте файл `config.py` со следующим содержимым:

```python
NETBOX_API_URL = "https://netbox.example.com/api"
NETBOX_API_TOKEN = "ваш_токен"
```

## 🧪 Требования

- Python 3.10+
- NetBox с доступным API

## 💾 База данных

Используется SQLite (файл `network.db` в корне проекта). При первом запуске все таблицы будут созданы автоматически.

## 📬 Обратная связь

Если вы нашли баг или хотите предложить улучшение — создайте issue или pull request.
