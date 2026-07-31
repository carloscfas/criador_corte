from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.models.video import VideoStatus


class VideoBase(BaseModel):
    original_filename: str
    file_size: Optional[int] = None


class VideoCreate(VideoBase):
    project_id: UUID


class VideoResponse(BaseModel):
    id: UUID
    project_id: UUID
    original_filename: str
    file_path: str
    file_size: Optional[int]
    duration: Optional[float]
    status: VideoStatus
    language: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    video_id: UUID
    filename: str
    status: str
    message: str


class UploadProgress(BaseModel):
    video_id: UUID
    progress: float  # 0-100
    status: VideoStatus
