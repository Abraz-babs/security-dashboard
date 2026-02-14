"""Database configuration for CITADEL KEBBI"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean
from datetime import datetime
import os

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/citadel")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class IntelReport(Base):
    """Stored intelligence reports"""
    __tablename__ = "intel_reports"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    description = Column(String(2000))
    source = Column(String(100))
    severity = Column(String(20))  # critical, high, medium, low
    category = Column(String(50))
    location_lga = Column(String(100))
    location_state = Column(String(50))
    lat = Column(Float)
    lon = Column(Float)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)
    is_archived = Column(Boolean, default=False)


class FireHotspot(Base):
    """NASA FIRMS fire data history"""
    __tablename__ = "fire_hotspots"
    
    id = Column(Integer, primary_key=True)
    satellite = Column(String(20))  # VIIRS, MODIS
    latitude = Column(Float)
    longitude = Column(Float)
    brightness = Column(Float)
    confidence = Column(String(20))
    acq_date = Column(DateTime)
    frp = Column(Float)  # Fire Radiative Power
    fetched_at = Column(DateTime, default=datetime.utcnow)


class UserActivity(Base):
    """Audit log for all user actions"""
    __tablename__ = "user_activity"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100))
    action = Column(String(100))  # login, generate_sitrep, view_intel
    details = Column(JSON)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)


class SITREPRecord(Base):
    """Generated SITREPs archive"""
    __tablename__ = "sitrep_records"
    
    id = Column(Integer, primary_key=True)
    period = Column(String(20))
    content = Column(String(5000))
    generated_by = Column(String(100))
    hotspot_count = Column(Integer)
    intel_count = Column(Integer)
    generated_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Database session dependency"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
