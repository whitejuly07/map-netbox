# events.py (в корне приложения)
from typing import Callable, Dict, List, Any

_listeners: Dict[str, List[Callable[..., Any]]] = {}

def subscribe(event_name: str, handler: Callable[..., Any]) -> None:
    """Подписаться на событие."""
    _listeners.setdefault(event_name, []).append(handler)

def emit(event_name: str, *args, **kwargs) -> None:
    """Вызвать всех подписчиков для события."""
    for handler in _listeners.get(event_name, []):
        try:
            handler(*args, **kwargs)
        except Exception:
            # Здесь можно добавить отдельный логгер для ошибок в обработчиках
            pass
