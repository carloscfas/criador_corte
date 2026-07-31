from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.video import Video, VideoStatus
from uuid import UUID


class VideoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, video: Video) -> Video:
        self.db.add(video)
        await self.db.commit()
        await self.db.refresh(video)
        return video

    async def get_by_id(self, video_id: UUID) -> Optional[Video]:
        result = await self.db.execute(select(Video).where(Video.id == video_id))
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: UUID) -> List[Video]:
        result = await self.db.execute(
            select(Video).where(Video.project_id == project_id).order_by(Video.created_at.desc())
        )
        return result.scalars().all()

    async def update(self, video: Video) -> Video:
        await self.db.commit()
        await self.db.refresh(video)
        return video

    async def update_status(self, video_id: UUID, status: VideoStatus) -> Optional[Video]:
        video = await self.get_by_id(video_id)
        if video:
            video.status = status
            await self.db.commit()
            await self.db.refresh(video)
        return video

    async def delete(self, video_id: UUID) -> bool:
        video = await self.get_by_id(video_id)
        if video:
            await self.db.delete(video)
            await self.db.commit()
            return True
        return False
