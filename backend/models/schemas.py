"""Pydantic schemas for CITADEL KEBBI"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: str
    user: dict


class ChatMessage(BaseModel):
    message: str
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str
    timestamp: str


class SITREPRequest(BaseModel):
    period: Optional[str] = "24h"
    include_ai_analysis: Optional[bool] = True


class ThreatData(BaseModel):
    level: str
    score: float
    active_threats: int
    total_incidents: int
    lga_data: list


class SatellitePass(BaseModel):
    satellite_name: str
    norad_id: int
    start_time: str
    end_time: str
    max_elevation: float
    direction: str


class FireHotspot(BaseModel):
    latitude: float
    longitude: float
    brightness: float
    confidence: str
    acq_date: str
    acq_time: str
    satellite: str
    frp: Optional[float] = None


class IntelReport(BaseModel):
    title: str
    source: str
    published_at: str
    description: str
    category: Optional[str] = "general"
    severity: Optional[str] = "medium"
    url: Optional[str] = None


class AnalysisRequest(BaseModel):
    dashboard_data: Optional[dict] = None
    focus_area: Optional[str] = None
