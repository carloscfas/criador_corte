from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    summary = Column(Text)
    key_topics = Column(JSONB)  # ["tecnologia", "ia", "futuro"]
    emotions_detected = Column(JSONB)  # [{"emotion": "excitement", "confidence": 0.9}]
    stories = Column(JSONB)  # [{start, end, title, summary}]
    jokes = Column(JSONB)  # [{start, end, text}]
    controversies = Column(JSONB)  # [{start, end, topic}]
    teachings = Column(JSONB)  # [{start, end, lesson}]
    viral_moments = Column(JSONB)  # [{start, end, score, reason}]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="ai_analysis")
