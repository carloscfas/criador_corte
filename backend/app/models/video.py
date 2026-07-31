from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class VideoStatus(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    duration = Column(Float)  # em segundos
    status = Column(Enum(VideoStatus), default=VideoStatus.UPLOADED)
    language = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="videos")
    audio_file = relationship("AudioFile", back_populates="video", uselist=False, cascade="all, delete-orphan")
    transcription = relationship("Transcription", back_populates="video", uselist=False, cascade="all, delete-orphan")
    clips = relationship("Clip", back_populates="video", cascade="all, delete-orphan")
    ai_analysis = relationship("AIAnalysis", back_populates="video", uselist=False, cascade="all, delete-orphan")
