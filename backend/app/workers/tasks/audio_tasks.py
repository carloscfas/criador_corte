from celery import shared_task
from app.workers.celery_app import celery_app


@shared_task(bind=True, name="audio.extract")
def extract_audio_task(self, video_id: str):
    """
    Extrai áudio do vídeo usando FFmpeg.
    """
    from app.workers.tasks.video_tasks import update_video_status
    from app.video.audio_extractor import AudioExtractor
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.repositories.video_repository import VideoRepository
    from app.repositories.audio_file_repository import AudioFileRepository
    from app.models.audio_file import AudioFile
    import asyncio
    
    # Atualizar status para PROCESSING
    update_video_status.delay(video_id, "processing")
    
    async def _extract():
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            video_repo = VideoRepository(session)
            audio_repo = AudioFileRepository(session)
            video = await video_repo.get_by_id(video_id)
            
            if not video:
                raise Exception(f"Video {video_id} not found")
            
            # Extrair áudio
            extractor = AudioExtractor()
            audio_result = extractor.extract(video.file_path)
            
            # Salvar AudioFile no banco
            audio_file = AudioFile(
                video_id=video.id,
                file_path=audio_result["path"],
                format=audio_result["format"],
                sample_rate=audio_result["sample_rate"],
                duration=audio_result["duration"]
            )
            await audio_repo.create(audio_file)
            
            return audio_result
    
    try:
        audio_result = asyncio.run(_extract())
        return {"video_id": video_id, "audio_path": audio_result["path"], "status": "success"}
    except Exception as e:
        update_video_status.delay(video_id, "failed")
        self.retry(exc=e, countdown=60, max_retries=3)
