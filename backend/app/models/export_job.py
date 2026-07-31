from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class ExportStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportPlatform(enum.Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    DOWNLOAD = "download"


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clip_id = Column(UUID(as_uuid=True), ForeignKey("clips.id"), nullable=False)
    platform = Column(Enum(ExportPlatform), nullable=False)
    status = Column(Enum(ExportStatus), default=ExportStatus.PENDING)
    resolution = Column(String)  # "1080x1920"
    format = Column(String)  # "mp4"
    fps = Column(Integer)  # 60
    file_path = Column(String)
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    clip = relationship("Clip", back_populates="export_jobs")
