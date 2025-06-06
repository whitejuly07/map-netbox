# Network Topology Frontend

Интерактивное веб-приложение для визуализации сетевой топологии. Фронтенд построен на **Vue 3** и использует **Vite** для сборки.

## 📦 Стек технологий

- [Vue 3](https://vuejs.org/)
- [Vite](https://vitejs.dev/)
- [vis-network](https://visjs.github.io/vis-network/) — визуализация сетевых графов
- [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket_API) — синхронизация в реальном времени
- [FastAPI](https://fastapi.tiangolo.com/) — бэкенд API (см. папку backend)

## 📁 Структура проекта

```
project-root/
├── public/
├── src/
│   ├── App.vue
│   ├── assets/
│   ├── components/
│   └── main.js
├── index.html
└── vite.config.js
```

## 🚀 Установка и запуск

### 1. Установка зависимостей

```bash
npm install
```

### 2. Запуск в режиме разработки

```bash
npm run dev
```

Приложение будет доступно по адресу [http://localhost:5173](http://localhost:5173)

### 3. Сборка для продакшена

```bash
npm run build
```

Собранные файлы будут в папке `dist/`.

## ⚙️ Переменные окружения

Создайте файл `.env` (если нужно) для настройки базового URL к API (по умолчанию используется `/api`).

```env
VITE_API_URL=http://localhost:8000/api
```

## 🔌 Связь с бэкендом

Фронтенд подключается к серверу FastAPI по следующим маршрутам:

- `GET /api/devices` — список устройств
- `GET /api/topology` — информация о подключениях
- `GET /api/positions` — текущие координаты узлов
- `POST /api/positions` — сохранение новых координат
- `POST /api/update` — синхронизация данных с NetBox
- `WebSocket /ws` — синхронизация в реальном времени

## 🧪 Требования

- Node.js >= 18
- npm >= 9

## 🛠 Полезные команды

```bash
# Линтинг
npm run lint

# Превью сборки
npm run preview
```

## 📬 Обратная связь

Если вы нашли баг или хотите предложить улучшение — создайте issue или pull request.
