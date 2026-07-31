from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transcription import Transcription
from uuid import UUID


class TranscriptionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, transcription: Transcription) -> Transcription:
        self.db.add(transcription)
        await self.db.commit()
        await self.db.refresh(transcription)
        return transcription

    async def get_by_id(self, transcription_id: UUID) -> Optional[Transcription]:
        result = await self.db.execute(select(Transcription).where(Transcription.id == transcription_id))
        return result.scalar_one_or_none()

    async def get_by_video(self, video_id: UUID) -> Optional[Transcription]:
        result = await self.db.execute(select(Transcription).where(Transcription.video_id == video_id))
        return result.scalar_one_or_none()

    async def update(self, transcription: Transcription) -> Transcription:
        await self.db.commit()
        await self.db.refresh(transcription)
        return transcription
