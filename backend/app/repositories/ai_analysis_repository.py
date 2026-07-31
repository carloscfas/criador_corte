from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ai_analysis import AIAnalysis
from uuid import UUID


class AIAnalysisRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, analysis: AIAnalysis) -> AIAnalysis:
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def get_by_id(self, analysis_id: UUID) -> Optional[AIAnalysis]:
        result = await self.db.execute(select(AIAnalysis).where(AIAnalysis.id == analysis_id))
        return result.scalar_one_or_none()

    async def get_by_video(self, video_id: UUID) -> Optional[AIAnalysis]:
        result = await self.db.execute(select(AIAnalysis).where(AIAnalysis.video_id == video_id))
        return result.scalar_one_or_none()

    async def update(self, analysis: AIAnalysis) -> AIAnalysis:
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis
