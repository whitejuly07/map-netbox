### crud.py
from sqlalchemy.orm import Session
from . import models

def upsert_device(db: Session, device_data):
    device = db.query(models.Device).filter_by(id=device_data["id"]).first()
    if device:
        device.name = device_data["name"]
        device.role = device_data["role"]
    else:
        device = models.Device(**device_data)
        db.add(device)

def upsert_position(db: Session, device_id: int, x: float, y: float):
    pos = db.query(models.Position).filter_by(device_id=device_id).first()
    if pos:
        pos.x = x
        pos.y = y
    else:
        pos = models.Position(device_id=device_id, x=x, y=y)
        db.add(pos)

def save_connection(db: Session, conn_data):
    conn = models.Connection(**conn_data)
    db.add(conn)

def clear_all(db: Session):
    db.query(models.Position).delete()
    db.query(models.Connection).delete()
    db.query(models.Device).delete()
    db.commit()

def get_devices(db: Session):
    return db.query(models.Device).all()

def get_positions(db: Session):
    return db.query(models.Position).all()

def get_connections(db: Session):
    return db.query(models.Connection).all()
# ----------------------
# CRUD для областей
# ----------------------
def get_regions(db: Session):
    return db.query(models.Region).all()

def upsert_region(db: Session, region_data: dict):
    region = db.query(models.Region).filter_by(id=region_data.get("id")).first()
    if region:
        region.name = region_data["name"]
        region.x = region_data["x"]
        region.y = region_data["y"]
        region.width = region_data["width"]
        region.height = region_data["height"]
        region.color = region_data["color"]
    else:
        region = models.Region(**region_data)
        db.add(region)

def delete_region(db: Session, region_id: int):
    db.query(models.Region).filter_by(id=region_id).delete()