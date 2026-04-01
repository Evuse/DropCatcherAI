from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    fqdn = Column(String, unique=True, index=True)
    status = Column(String, default="SCHEDULED") # SCHEDULED, DROP_WINDOW, REGISTERED_BY_US, LOST
    expected_drop_at = Column(DateTime)
    auto_start_window_seconds = Column(Integer, default=60)
    burst_duration_seconds = Column(Integer, default=120)
    interval_ms = Column(Integer, default=500)
    selected_providers = Column(String, default="") # CSV: dynadot,openprovider
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, index=True)
    status = Column(String, default="RUNNING") # RUNNING, SUCCESS, LOST
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    winner_registrar = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, index=True)
    registrar_name = Column(String)
    attempted_at = Column(DateTime, server_default=func.now())
    success = Column(Boolean, default=False)
    latency_ms = Column(Integer, default=0)
    message = Column(Text, nullable=True)
    raw_response = Column(Text, nullable=True)
