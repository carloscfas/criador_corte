from celery import shared_task
from app.workers.celery_app import celery_app


@shared_task(bind=True, name="analysis.analyze")
def analyze_transcription_task(self, previous_result):
    """
    Analisa a transcrição com IA (Gemini) para encontrar melhores momentos.
    previous_result: {"video_id": str, "transcription": dict, "status": str}
    """
    from app.workers.tasks.video_tasks import update_video_status
    from app.ai.analysis_service import AnalysisService
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.core.config import settings
    from app.repositories.ai_analysis_repository import AIAnalysisRepository
    from app.repositories.clip_repository import ClipRepository
    from app.repositories.video_repository import VideoRepository
    from app.repositories.transcription_repository import TranscriptionRepository
    from app.models.ai_analysis import AIAnalysis
    from app.models.clip import Clip
    import asyncio
    
    video_id = previous_result["video_id"]
    transcription = previous_result["transcription"]
    
    # Atualizar status para ANALYZING
    update_video_status.delay(video_id, "analyzing")
    
    async def _analyze():
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            video_repo = VideoRepository(session)
            analysis_repo = AIAnalysisRepository(session)
            clip_repo = ClipRepository(session)
            transcription_repo = TranscriptionRepository(session)
            
            video = await video_repo.get_by_id(video_id)
            if not video:
                raise Exception(f"Video {video_id} not found")
            
            # Analisar transcrição com Gemini
            analysis_service = AnalysisService()
            analysis = await analysis_service.analyze(transcription)
            
            # Salvar AIAnalysis no banco
            ai_analysis = AIAnalysis(
                video_id=video.id,
                summary=analysis.get("summary"),
                key_topics=analysis.get("key_topics"),
                emotions_detected=analysis.get("emotions_detected"),
                stories=analysis.get("stories"),
                jokes=analysis.get("jokes"),
                controversies=analysis.get("controversies"),
                teachings=analysis.get("teachings"),
                viral_moments=analysis.get("viral_moments")
            )
            await analysis_repo.create(ai_analysis)
            
            # Gerar clips baseados na análise com Gemini
            clips_suggestions = await analysis_service.generate_clips_from_analysis(analysis)
            
            # Salvar clips no banco e cortar vídeos automaticamente
            from app.video.export_service import VideoExportService
            video_export_service = VideoExportService()
            
            for clip_data in clips_suggestions:
                clip = Clip(
                    video_id=video.id,
                    title=clip_data.get("summary") or clip_data["text"][:50],
                    description=clip_data.get("reason") or clip_data.get("lesson", ""),
                    start_time=clip_data["start"],
                    end_time=clip_data["end"],
                    duration=clip_data["duration"],
                    viral_score=clip_data["score"],
                    category=clip_data["type"],
                    segments=[clip_data]
                )
                created_clip = await clip_repo.create(clip)
                
                # Cortar o vídeo automaticamente para este clip
                try:
                    clip_output_path = video_export_service.export_clip(
                        video_path=video.file_path,
                        start_time=clip_data["start"],
                        end_time=clip_data["end"],
                        resolution="1080x1920",
                        fps=30,
                        format="mp4"
                    )
                    
                    # Gerar thumbnail
                    thumbnail_path = video_export_service.generate_thumbnail(
                        video_path=video.file_path,
                        timestamp=clip_data["start"] + (clip_data["duration"] / 2)
                    )
                    
                    # Atualizar clip com caminhos dos arquivos gerados
                    created_clip.file_path = clip_output_path
                    created_clip.thumbnail_path = thumbnail_path
                    await clip_repo.update(created_clip)
                    
                except Exception as e:
                    # Se falhar o corte, continuar com os próximos clips
                    print(f"Failed to cut video for clip {created_clip.id}: {str(e)}")
                    continue
            
            return analysis
    
    try:
        analysis = asyncio.run(_analyze())
        
        # Atualizar status para COMPLETED
        update_video_status.delay(video_id, "completed")
        
        return {
            "video_id": video_id,
            "analysis": analysis,
            "status": "success"
        }
    except Exception as e:
        update_video_status.delay(video_id, "failed")
        self.retry(exc=e, countdown=60, max_retries=3)
