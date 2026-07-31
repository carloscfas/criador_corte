from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class UploadHistory(Base):
    __tablename__ = "upload_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"))
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer)
    status = Column(String)  # success, failed, cancelled
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
