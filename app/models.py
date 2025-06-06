### models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)
    positions = relationship("Position", back_populates="device", uselist=False)


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), unique=True)
    x = Column(Float)
    y = Column(Float)

    device = relationship("Device", back_populates="positions")


class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    cable_id = Column(Integer)
    
    # добавь эти поля:
    port_a_id = Column(Integer)
    port_a_device = Column(String)
    port_a_name = Column(String)
    port_b_id = Column(Integer)
    port_b_device = Column(String)
    port_b_name = Column(String)

# Новая модель для областей (regions)
class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    color = Column(String, default="#b8b8b853")  # цвет фона, можно менять