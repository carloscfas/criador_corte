from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.clip import Clip
from uuid import UUID


class ClipRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, clip: Clip) -> Clip:
        self.db.add(clip)
        await self.db.commit()
        await self.db.refresh(clip)
        return clip

    async def get_by_id(self, clip_id: UUID) -> Optional[Clip]:
        result = await self.db.execute(select(Clip).where(Clip.id == clip_id))
        return result.scalar_one_or_none()

    async def get_by_video(self, video_id: UUID) -> List[Clip]:
        result = await self.db.execute(
            select(Clip)
            .where(Clip.video_id == video_id)
            .order_by(Clip.viral_score.desc())
        )
        return result.scalars().all()

    async def update(self, clip: Clip) -> Clip:
        await self.db.commit()
        await self.db.refresh(clip)
        return clip

    async def approve(self, clip_id: UUID) -> Optional[Clip]:
        clip = await self.get_by_id(clip_id)
        if clip:
            clip.is_approved = True
            await self.db.commit()
            await self.db.refresh(clip)
        return clip
