from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class ClipBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: float
    end_time: float
    category: Optional[str] = None


class ClipCreate(ClipBase):
    video_id: UUID


class ClipUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_approved: Optional[bool] = None


class ClipResponse(BaseModel):
    id: UUID
    video_id: UUID
    title: Optional[str]
    description: Optional[str]
    start_time: float
    end_time: float
    duration: Optional[float]
    viral_score: Optional[int]
    category: Optional[str]
    tags: Optional[List[str]]
    is_approved: bool
    file_path: Optional[str]
    thumbnail_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClipListResponse(BaseModel):
    clips: List[ClipResponse]
    total: int
