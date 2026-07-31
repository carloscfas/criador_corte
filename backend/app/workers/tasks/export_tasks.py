from celery import shared_task
from app.workers.celery_app import celery_app


@shared_task(bind=True, name="export.clip")
def export_clip_task(self, job_id: str):
    """
    Processa um job de exportação de clip.
    """
    from app.workers.tasks.video_tasks import update_video_status
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.services.export_service import ExportService
    import asyncio
    
    async def _export():
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            export_service = ExportService(session)
            output_path = await export_service.process_export_job(job_id)
            return output_path
    
    try:
        output_path = asyncio.run(_export())
        return {"job_id": job_id, "output_path": output_path, "status": "success"}
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
