from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.models.export_job import ExportPlatform, ExportStatus


class ExportRequest(BaseModel):
    clip_id: UUID
    platform: ExportPlatform
    resolution: str = Field(default="1080x1920", description="Resolução (ex: 1080x1920 para 9:16)")
    format: str = Field(default="mp4")
    fps: int = Field(default=60, ge=1, le=120)
    add_subtitles: bool = False


class ExportResponse(BaseModel):
    job_id: UUID
    clip_id: UUID
    platform: ExportPlatform
    status: ExportStatus
    message: str


class ExportJobResponse(BaseModel):
    id: UUID
    clip_id: UUID
    platform: ExportPlatform
    status: ExportStatus
    resolution: Optional[str]
    format: Optional[str]
    fps: Optional[int]
    file_path: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
