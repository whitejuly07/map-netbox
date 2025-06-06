import httpx
from .config import NETBOX_API_URL, NETBOX_API_TOKEN

HEADERS = {
    "Authorization": f"Token {NETBOX_API_TOKEN}"
}

async def fetch(endpoint: str):
    async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(30.0)) as client:
        url = f"{NETBOX_API_URL}/{endpoint.lstrip('/')}"
        response = await client.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()

async def get_devices():
    return await fetch("/dcim/devices/?limit=1000&_depth=1")

async def get_interfaces():
    return await fetch("/dcim/interfaces/?limit=1000")

async def get_cables():
    return await fetch("/dcim/cables/?_depth=1&limit=1000")

async def get_sites():
    """
    Получить все Sites (локации) из NetBox.
    Мы используем endpoint /dcim/sites/,
    поскольку в NetBox Sites — это основная сущность «локаций».
    Если у вас версия NetBox ≥3.6 с ресурсом /dcim/locations/,
    можно аналогично добавить get_locations().
    """
    return await fetch("/dcim/sites/?limit=1000&_depth=1")