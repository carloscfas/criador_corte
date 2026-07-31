from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.export_job import ExportJob, ExportStatus
from uuid import UUID


class ExportJobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, job: ExportJob) -> ExportJob:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_by_id(self, job_id: UUID) -> Optional[ExportJob]:
        result = await self.db.execute(select(ExportJob).where(ExportJob.id == job_id))
        return result.scalar_one_or_none()

    async def get_by_clip(self, clip_id: UUID) -> List[ExportJob]:
        result = await self.db.execute(
            select(ExportJob)
            .where(ExportJob.clip_id == clip_id)
            .order_by(ExportJob.created_at.desc())
        )
        return result.scalars().all()

    async def update(self, job: ExportJob) -> ExportJob:
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def update_status(self, job_id: UUID, status: ExportStatus, file_path: Optional[str] = None, error_message: Optional[str] = None) -> Optional[ExportJob]:
        job = await self.get_by_id(job_id)
        if job:
            job.status = status
            if file_path:
                job.file_path = file_path
            if error_message:
                job.error_message = error_message
            if status == ExportStatus.COMPLETED:
                from datetime import datetime
                job.completed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(job)
        return job
