from celery import shared_task
from app.workers.celery_app import celery_app
from app.models.video import VideoStatus


@shared_task(bind=True, name="video.process_workflow")
def process_video_workflow(self, video_id: str):
    """
    Workflow principal de processamento de vídeo.
    Orquestra todas as tasks em sequência.
    """
    from app.workers.tasks.audio_tasks import extract_audio_task
    from app.workers.tasks.transcription_tasks import transcribe_audio_task
    from app.workers.tasks.analysis_tasks import analyze_transcription_task
    
    # Chain: extract_audio -> transcribe -> analyze
    workflow = (
        extract_audio_task.s(video_id) |
        transcribe_audio_task.s() |
        analyze_transcription_task.s()
    )
    
    return workflow()


@shared_task(name="video.update_status")
def update_video_status(video_id: str, status: str):
    """
    Atualiza o status do vídeo no banco de dados.
    """
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.repositories.video_repository import VideoRepository
    from app.models.video import VideoStatus
    
    # Criar sessão assíncrona
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    import asyncio
    
    async def _update():
        async with async_session() as session:
            video_repo = VideoRepository(session)
            video_status = VideoStatus(status)
            await video_repo.update_status(video_id, video_status)
    
    asyncio.run(_update())
    return {"video_id": video_id, "status": status}
