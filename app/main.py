# backend/main.py

from fastapi import FastAPI, Depends, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from .database import SessionLocal, engine
from . import models, crud
from .services.netbox_sync import sync_from_netbox
from .services.regions import save_region, list_regions
from .events import emit

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- WebSocket для уведомлений ---
clients = set()
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            # ретранслируем
            for c in clients:
                if c != ws:
                    await c.send_text(msg)
    except:
        clients.remove(ws)

# --- Синхрон: устройства и связи ---
@app.post("/api/update")
async def update_from_netbox(db: Session = Depends(get_db)):
    await sync_from_netbox(db)
    for ws in list(clients):
        try:
            await ws.send_text("netbox_updated")
        except Exception as e:
            logger.error("WS broadcast error: %s", e)
    return {"status": "updated"}

# --- Стандартные GET ---
@app.get("/api/devices")
def api_devices(db: Session = Depends(get_db)):
    return crud.get_devices(db)

@app.get("/api/positions")
def api_positions(db: Session = Depends(get_db)):
    return { str(p.device_id): {"x": p.x, "y": p.y} for p in crud.get_positions(db) }

@app.get("/api/topology")
def api_topology(db: Session = Depends(get_db)):
    return [
        {
            "cable_id": c.cable_id,
            "port_a": {"device": c.port_a_device, "name": c.port_a_name},
            "port_b": {"device": c.port_b_device, "name": c.port_b_name}
        } for c in crud.get_connections(db)
    ]

@app.post("/api/positions")
def api_save_positions(pos: dict, db: Session = Depends(get_db)):
    for dev_id, coord in pos.items():
        crud.upsert_position(db, int(dev_id), coord["x"], coord["y"])
    db.commit()
    return {"status": "ok"}

# --- Новое: модели Pydantic для Region ---
class RegionIn(BaseModel):
    id: int = None
    name: str
    x: float
    y: float
    width: float
    height: float
    color: str

# GET всех областей
@app.get("/api/regions")
def api_get_regions(db: Session = Depends(get_db)):
    return list_regions(db)

# POST создания/обновления области
@app.post("/api/regions")
def api_post_region(region: RegionIn, db: Session = Depends(get_db)):
    save_region(db, region.dict())
    # уведомим frontend
    for ws in list(clients):
        try:
            ws.send_text("region_updated")
        except:
            pass
    return {"status": "ok"}

# DELETE области
@app.delete("/api/regions/{region_id}")
def api_delete_region(region_id: int, db: Session = Depends(get_db)):
    crud.delete_region(db, region_id)
    return {"status": "deleted"}
