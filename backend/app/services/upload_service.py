import os
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
from app.schemas.video import VideoCreate, VideoResponse, UploadResponse
from app.models.video import Video, VideoStatus
from app.models.upload_history import UploadHistory
from app.repositories.video_repository import VideoRepository
from app.repositories.upload_history_repository import UploadHistoryRepository
from app.core.config import settings


class UploadService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.upload_history_repo = UploadHistoryRepository(db)

    async def upload_video(
        self,
        user_id: str,
        project_id: str,
        file: UploadFile
    ) -> UploadResponse:
        # Validação de extensão
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension. Allowed: {settings.VIDEO_EXTENSIONS}"
            )

        # Criar diretório de upload se não existir
        upload_dir = os.path.join(settings.UPLOAD_DIR, user_id)
        os.makedirs(upload_dir, exist_ok=True)

        # Gerar nome único para o arquivo
        file_id = str(uuid.uuid4())
        file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")

        # Salvar arquivo
        try:
            file_size = 0
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    buffer.write(chunk)
                    file_size += len(chunk)

                    # Validar tamanho máximo
                    if file_size > settings.MAX_UPLOAD_SIZE:
                        os.remove(file_path)
                        raise HTTPException(
                            status_code=400,
                            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
                        )
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

        # Criar registro no banco de dados
        video = Video(
            project_id=project_id,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            status=VideoStatus.UPLOADED
        )
        created_video = await self.video_repo.create(video)

        # Registrar histórico de upload
        upload_history = UploadHistory(
            user_id=user_id,
            video_id=created_video.id,
            original_filename=file.filename,
            file_size=file_size,
            status="success"
        )
        await self.upload_history_repo.create(upload_history)

        # Disparar workflow de processamento assíncrono
        from app.workers.tasks.video_tasks import process_video_workflow
        process_video_workflow.delay(str(created_video.id))

        return UploadResponse(
            video_id=created_video.id,
            filename=file.filename,
            status="success",
            message="Video uploaded successfully"
        )

    async def get_video(self, video_id: str, user_id: str) -> VideoResponse:
        video = await self.video_repo.get_by_id(video_id)
        if not video:
            raise ValueError("Video not found")
        
        # Verificar se o usuário tem acesso (via project)
        # TODO: Implementar verificação de permissão
        return VideoResponse.model_validate(video)
