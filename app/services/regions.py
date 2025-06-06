# backend/services/regions.py

import logging
from sqlalchemy.orm import Session
from .. import crud, models
from ..events import emit

logger = logging.getLogger(__name__)

def save_region(db: Session, region_data: dict):
    """
    Сохраняет или обновляет область.
    После сохранения шлёт событие 'region_updated'.
    """
    crud.upsert_region(db, region_data)
    db.commit()
    emit("region_updated", region_data)
    logger.info("Region saved: %s", region_data)

def list_regions(db: Session):
    """
    Возвращает все области.
    """
    return crud.get_regions(db)
