from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audio_file import AudioFile
from uuid import UUID


class AudioFileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, audio_file: AudioFile) -> AudioFile:
        self.db.add(audio_file)
        await self.db.commit()
        await self.db.refresh(audio_file)
        return audio_file

    async def get_by_id(self, audio_id: UUID) -> Optional[AudioFile]:
        result = await self.db.execute(select(AudioFile).where(AudioFile.id == audio_id))
        return result.scalar_one_or_none()

    async def get_by_video(self, video_id: UUID) -> Optional[AudioFile]:
        result = await self.db.execute(select(AudioFile).where(AudioFile.video_id == video_id))
        return result.scalar_one_or_none()

    async def update(self, audio_file: AudioFile) -> AudioFile:
        await self.db.commit()
        await self.db.refresh(audio_file)
        return audio_file
