from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.upload_history import UploadHistory
from uuid import UUID


class UploadHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, history: UploadHistory) -> UploadHistory:
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_by_user(self, user_id: UUID) -> List[UploadHistory]:
        result = await self.db.execute(
            select(UploadHistory)
            .where(UploadHistory.user_id == user_id)
            .order_by(UploadHistory.created_at.desc())
        )
        return result.scalars().all()
