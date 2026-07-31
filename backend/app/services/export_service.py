from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.export import ExportRequest, ExportResponse, ExportJobResponse
from app.models.export_job import ExportJob, ExportStatus, ExportPlatform
from app.repositories.export_job_repository import ExportJobRepository
from app.repositories.clip_repository import ClipRepository
from app.repositories.video_repository import VideoRepository
from app.video.export_service import VideoExportService
from app.video.subtitle_service import SubtitleService
from uuid import UUID
import os


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.export_job_repo = ExportJobRepository(db)
        self.clip_repo = ClipRepository(db)
        self.video_repo = VideoRepository(db)
        self.video_export_service = VideoExportService()
        self.subtitle_service = SubtitleService()

    async def create_export_job(self, user_id: str, export_request: ExportRequest) -> ExportResponse:
        """
        Cria um job de exportação e dispara o processamento assíncrono.
        """
        # Verificar se o clip existe
        clip = await self.clip_repo.get_by_id(export_request.clip_id)
        if not clip:
            raise ValueError("Clip not found")

        # Verificar permissão (via video/project)
        video = await self.video_repo.get_by_id(clip.video_id)
        if not video:
            raise ValueError("Video not found")

        # TODO: Verificar permissão do usuário

        # Criar job de exportação
        job = ExportJob(
            clip_id=export_request.clip_id,
            platform=export_request.platform,
            status=ExportStatus.PENDING,
            resolution=export_request.resolution,
            format=export_request.format,
            fps=export_request.fps
        )
        created_job = await self.export_job_repo.create(job)

        # Disparar task assíncrona
        from app.workers.tasks.export_tasks import export_clip_task
        export_clip_task.delay(str(created_job.id))

        return ExportResponse(
            job_id=created_job.id,
            clip_id=created_job.clip_id,
            platform=created_job.platform,
            status=created_job.status,
            message="Export job created successfully"
        )

    async def get_export_job(self, job_id: UUID) -> ExportJobResponse:
        """
        Retorna o status de um job de exportação.
        """
        job = await self.export_job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Export job not found")
        return ExportJobResponse.model_validate(job)

    async def get_clip_exports(self, clip_id: UUID) -> list:
        """
        Retorna todos os jobs de exportação de um clip.
        """
        jobs = await self.export_job_repo.get_by_clip(clip_id)
        return [ExportJobResponse.model_validate(job) for job in jobs]

    async def process_export_job(self, job_id: UUID) -> str:
        """
        Processa um job de exportação (síncrono, usado pela task).
        """
        job = await self.export_job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Export job not found")

        # Atualizar status para PROCESSING
        await self.export_job_repo.update_status(job_id, ExportStatus.PROCESSING)

        try:
            # Obter clip e vídeo
            clip = await self.clip_repo.get_by_id(job.clip_id)
            video = await self.video_repo.get_by_id(clip.video_id)

            # Gerar legendas se necessário
            subtitle_path = None
            if job.platform != ExportPlatform.DOWNLOAD:
                # Para redes sociais, adicionar legendas automaticamente
                from app.repositories.transcription_repository import TranscriptionRepository
                transcription_repo = TranscriptionRepository(self.db)
                transcription = await transcription_repo.get_by_video(video.id)
                
                if transcription and transcription.segments:
                    subtitle_path = os.path.join("uploads", "subtitles", f"{job_id}.ass")
                    self.subtitle_service.generate_ass(transcription.segments, subtitle_path, style="karaoke")

            # Exportar vídeo
            output_path = self.video_export_service.export_clip(
                video_path=video.file_path,
                start_time=clip.start_time,
                end_time=clip.end_time,
                resolution=job.resolution,
                fps=job.fps,
                format=job.format,
                add_subtitles=subtitle_path is not None,
                subtitle_path=subtitle_path
            )

            # Gerar thumbnail
            thumbnail_path = self.video_export_service.generate_thumbnail(
                video_path=video.file_path,
                timestamp=clip.start_time + (clip.duration / 2)
            )

            # Atualizar clip com caminhos
            clip.file_path = output_path
            clip.thumbnail_path = thumbnail_path
            
            # Gerar SEO se ainda não foi gerado
            if not clip.title or not clip.description or not clip.tags:
                from app.ai.seo_service import SEOService
                from app.repositories.transcription_repository import TranscriptionRepository
                
                transcription_repo = TranscriptionRepository(self.db)
                transcription = await transcription_repo.get_by_video(video.id)
                
                if transcription:
                    seo_service = SEOService()
                    # Extrair texto do clip
                    clip_text = ""
                    for segment in transcription.segments:
                        if segment['start'] >= clip.start_time and segment['end'] <= clip.end_time:
                            clip_text += segment['text'] + " "
                    
                    if clip_text:
                        seo_content = await seo_service.generate_complete_seo(
                            clip_text,
                            clip.category or "geral"
                        )
                        
                        if not clip.title and seo_content['titles']:
                            clip.title = seo_content['titles'][0]
                        if not clip.description:
                            clip.description = seo_content['description']
                        if not clip.tags:
                            clip.tags = seo_content['hashtags']
            
            await self.clip_repo.update(clip)

            # Atualizar job como COMPLETED
            await self.export_job_repo.update_status(job_id, ExportStatus.COMPLETED, output_path)

            return output_path

        except Exception as e:
            # Atualizar job como FAILED
            await self.export_job_repo.update_status(job_id, ExportStatus.FAILED, error_message=str(e))
            raise
