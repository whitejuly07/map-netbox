# backend/services/netbox_sync.py
import logging
from sqlalchemy.orm import Session

from .. import models, crud
from ..netbox_client import get_devices, get_cables, get_sites
from ..events import emit

logger = logging.getLogger(__name__)

async def sync_from_netbox(db: Session) -> None:
    """
    Синхронизирует данные из NetBox: устройства, связи и локации (Sites → Regions).
    Генерирует события:
      - 'sync_started'
      - 'device_added'
      - 'connection_added'
      - 'region_added'
      - 'sync_completed'
    """
    logger.info("Начата синхронизация из NetBox")
    emit("sync_started")

    # 1. Очистка старых данных
    db.query(models.Device).delete()
    db.query(models.Connection).delete()
    db.query(models.Region).delete()
    db.commit()

    # 2. Синхронизация устройств
    devices_raw = await get_devices()
    for dev in devices_raw.get("results", []):
        device = models.Device(
            id=dev["id"],
            name=dev["name"],
            role=dev.get("role", {}).get("name", "unknown")
        )
        db.add(device)
        emit("device_added", dev)
    db.commit()
    logger.info("Устройства сохранены: %d", len(devices_raw.get("results", [])))

    # 3. Синхронизация связей
    cables_raw = await get_cables()
    count_conn = 0
    for cable in cables_raw.get("results", []):
        try:
            a_term = cable.get("a_terminations", [])
            b_term = cable.get("b_terminations", [])
            if not a_term or not b_term:
                continue
            ia = a_term[0].get("object", {})
            ib = b_term[0].get("object", {})
            conn = models.Connection(
                cable_id=cable["id"],
                port_a_id=ia.get("id"),
                port_a_name=ia.get("name", ""),
                port_a_device=ia.get("device", {}).get("name", ""),
                port_b_id=ib.get("id"),
                port_b_name=ib.get("name", ""),
                port_b_device=ib.get("device", {}).get("name", "")
            )
            db.add(conn)
            emit("connection_added", {"cable": cable})
            count_conn += 1
        except Exception as e:
            logger.error("Ошибка обработки кабеля %s: %s", cable.get("id"), e)
    db.commit()
    logger.info("Связи сохранены: %d", count_conn)

    # 4. Синхронизация областей (Sites → Regions)
    sites_raw = await get_sites()
    for idx, site in enumerate(sites_raw.get("results", [])):
        # Располагаем зоны горизонтально с отступом
        region_data = {
            "id": site["id"],
            "name": site.get("name", ""),
            "x": 50 + idx * 550,
            "y": 50,
            "width": 500,
            "height": 400,
            "color": "#ccffcc"
        }
        crud.upsert_region(db, region_data)
        emit("region_added", region_data)
    db.commit()
    logger.info("Области синхронизированы: %d", len(sites_raw.get("results", [])))

    # Завершаем синхронизацию
    emit("sync_completed")
    logger.info("Синхронизация из NetBox завершена")
