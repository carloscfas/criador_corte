from celery import shared_task
from app.workers.celery_app import celery_app


@shared_task(bind=True, name="trans audio.transcribe")
def transcribe_audio_task(self, previous_result):
    """
    Transcreve o áudio usando Whisper.
    previous_result: {"video_id": str, "audio_path": str, "status": str}
    """
    from app.workers.tasks.video_tasks import update_video_status
    from app.ai.whisper_service import WhisperService
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.repositories.transcription_repository import TranscriptionRepository
    from app.repositories.video_repository import VideoRepository
    from app.models.transcription import Transcription
    import asyncio
    
    video_id = previous_result["video_id"]
    audio_path = previous_result["audio_path"]
    
    # Atualizar status para TRANSCRIBING
    update_video_status.delay(video_id, "transcribing")
    
    async def _transcribe():
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            video_repo = VideoRepository(session)
            transcription_repo = TranscriptionRepository(session)
            video = await video_repo.get_by_id(video_id)
            
            if not video:
                raise Exception(f"Video {video_id} not found")
            
            # Transcrever
            whisper_service = WhisperService()
            transcription = await whisper_service.transcribe(audio_path)
            
            # Salvar Transcription no banco
            transcription_record = Transcription(
                video_id=video.id,
                text=transcription["text"],
                segments=transcription["segments"],
                language=transcription["language"],
                confidence=transcription.get("confidence"),
                duration=transcription["duration"]
            )
            await transcription_repo.create(transcription_record)
            
            # Atualizar vídeo com idioma detectado
            video.language = transcription["language"]
            await video_repo.update(video)
            
            return transcription
    
    try:
        transcription = asyncio.run(_transcribe())
        return {
            "video_id": video_id,
            "transcription": transcription,
            "status": "success"
        }
    except Exception as e:
        update_video_status.delay(video_id, "failed")
        self.retry(exc=e, countdown=60, max_retries=3)
