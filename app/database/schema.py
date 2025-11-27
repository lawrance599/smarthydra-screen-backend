from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, JSON
from sqlalchemy.sql import func


class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


class AlertType(str, Enum):
    WATER_LEVEL = "water_level"
    RAINFALL = "rainfall"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class BaseTimestampModel(SQLModel):
    """基础时间戳模型"""

    created_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    )


class User(BaseTimestampModel, table=True):
    """用户模型"""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)


class City(SQLModel, table=True):
    """城市模型"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    code: str = Field(index=True)


class Station(BaseTimestampModel, table=True):
    """测站模型"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    code: str = Field(index=True)
    city_id: int = Field(default=None, index=True)
    latitude: float
    longitude: float
    water_level_threshold: Optional[float] = Field(default=None)
    rainfall_threshold: Optional[float] = Field(default=None)
    is_active: bool = Field(default=True)


class WaterLevelData(SQLModel, table=True):
    """水表数据模型"""

    id: Optional[int] = Field(default=None, primary_key=True)
    station_id: int = Field(default=None, index=True)
    value: float
    measure_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )


class RainfallData(SQLModel, table=True):
    """雨量数据模型"""

    id: Optional[int] = Field(default=None, primary_key=True)
    station_id: int = Field(default=None, index=True)
    value: float
    measure_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

class Alert(SQLModel, table=True):
    """报警模型"""

    id: Optional[int] = Field(default=None, primary_key=True)
    station_id: int = Field(default=None, index=True)
    alert_type: AlertType
    alert_message: str
    status: AlertStatus
    
    trigger_value: float
    threshold: float
    trigger_data_id: int
    
    trigger_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    revolved_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
