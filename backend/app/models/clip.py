from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Clip(Base):
    __tablename__ = "clips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    title = Column(String)
    description = Column(Text)
    start_time = Column(Float, nullable=False)  # em segundos
    end_time = Column(Float, nullable=False)  # em segundos
    duration = Column(Float)
    viral_score = Column(Integer)  # 0-100
    category = Column(String)
    tags = Column(JSONB)  # ["negócios", "motivação"]
    segments = Column(JSONB)  # segmentos da transcrição incluídos
    is_approved = Column(Boolean, default=False)
    file_path = Column(String)  # caminho do vídeo gerado
    thumbnail_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="clips")
    export_jobs = relationship("ExportJob", back_populates="clip", cascade="all, delete-orphan")
