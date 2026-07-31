from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.database import get_db
from app.schemas.video import VideoResponse, UploadResponse
from app.services.upload_service import UploadService
from app.services.youtube_service import YouTubeService
from app.core.deps import get_current_user_id
from app.core.config import settings
from app.models.video import Video
from app.models.clip import Clip
from app.models.audio_file import AudioFile
from app.models.ai_analysis import AIAnalysis
from app.models.transcription import Transcription
from app.models.export_job import ExportJob
from app.models.upload_history import UploadHistory

router = APIRouter(prefix="/videos", tags=["videos"])


class YouTubeURLRequest(BaseModel):
    url: str


@router.post("/youtube/{project_id}", response_model=dict)
async def download_from_youtube(
    project_id: str,
    request: YouTubeURLRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Baixa um vídeo do YouTube e o processa automaticamente.
    """
    try:
        youtube_service = YouTubeService(upload_dir=settings.UPLOAD_DIR)
        result = youtube_service.download_video(request.url, project_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=result.get('error', 'Failed to download video')
            )
        
        # Criar registro no banco de dados
        from app.models.video import Video, VideoStatus
        from app.models.upload_history import UploadHistory
        from app.repositories.video_repository import VideoRepository
        from app.repositories.upload_history_repository import UploadHistoryRepository
        import os
        
        video_repo = VideoRepository(db)
        upload_history_repo = UploadHistoryRepository(db)
        
        # Obter tamanho do arquivo
        file_size = os.path.getsize(result['filepath']) if os.path.exists(result['filepath']) else 0
        
        video = Video(
            project_id=project_id,
            original_filename=result['filename'],
            file_path=result['filepath'],
            file_size=file_size,
            duration=result.get('duration'),
            status=VideoStatus.UPLOADED
        )
        created_video = await video_repo.create(video)
        
        # Registrar histórico de upload
        upload_history = UploadHistory(
            user_id=user_id,
            video_id=created_video.id,
            original_filename=result['filename'],
            file_size=file_size,
            status="success"
        )
        await upload_history_repo.create(upload_history)
        
        # Não dispara mais o workflow de processamento (IA desativada)
        # O vídeo fica apenas baixado e pronto para uso
        
        # Retornar sucesso com informações do vídeo baixado
        return {
            'success': True,
            'message': 'Video downloaded successfully',
            'video_id': str(created_video.id),
            'filename': result['filename'],
            'filepath': result['filepath'],
            'title': result['title'],
            'duration': result['duration'],
            'platform': result.get('platform', 'youtube')
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/info/youtube")
async def get_youtube_video_info(request: YouTubeURLRequest):
    """
    Obtém informações sobre um vídeo do YouTube sem baixar.
    """
    try:
        youtube_service = YouTubeService()
        result = youtube_service.get_video_info(request.url)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to get video info')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/project/{project_id}")
async def get_videos_by_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém todos os vídeos de um projeto específico.
    """
    try:
        from app.repositories.video_repository import VideoRepository
        from app.models.video import Video
        
        video_repo = VideoRepository(db)
        videos = await video_repo.get_by_project(project_id)
        
        # Filtrar por usuário se necessário
        return [
            {
                'id': str(video.id),
                'original_filename': video.original_filename,
                'duration': video.duration,
                'status': video.status,
                'created_at': video.created_at.isoformat() if video.created_at else None,
            }
            for video in videos
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/upload/{project_id}", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    project_id: str,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        upload_service = UploadService(db)
        return await upload_service.upload_video(user_id, project_id, file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        upload_service = UploadService(db)
        return await upload_service.get_video(video_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Exclui um vídeo e todos os seus arquivos associados.
    """
    try:
        from app.repositories.video_repository import VideoRepository
        from app.repositories.clip_repository import ClipRepository
        import os
        
        video_repo = VideoRepository(db)
        clip_repo = ClipRepository(db)
        
        video = await video_repo.get_by_id(UUID(video_id))
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        # Deletar arquivos físicos
        files_to_delete = []
        
        # Arquivo de vídeo original
        if video.file_path and os.path.exists(video.file_path):
            files_to_delete.append(video.file_path)
        
        # Arquivos de clips
        clips = await clip_repo.get_by_video(UUID(video_id))
        for clip in clips:
            if clip.file_path and os.path.exists(clip.file_path):
                files_to_delete.append(clip.file_path)
            if clip.thumbnail_path and os.path.exists(clip.thumbnail_path):
                files_to_delete.append(clip.thumbnail_path)
        
        # Deletar arquivos
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete file {file_path}: {str(e)}")
        
        # Deletar registros relacionados manualmente (em ordem de dependência)
        # 1. Deletar export_jobs
        await db.execute(delete(ExportJob).where(ExportJob.clip_id.in_(
            select(Clip.id).where(Clip.video_id == UUID(video_id))
        )))
        
        # 2. Deletar clips
        await db.execute(delete(Clip).where(Clip.video_id == UUID(video_id)))
        
        # 3. Deletar AI analysis
        await db.execute(delete(AIAnalysis).where(AIAnalysis.video_id == UUID(video_id)))
        
        # 4. Deletar transcription
        await db.execute(delete(Transcription).where(Transcription.video_id == UUID(video_id)))
        
        # 5. Deletar audio_file
        await db.execute(delete(AudioFile).where(AudioFile.video_id == UUID(video_id)))
        
        # 6. Deletar upload_history
        await db.execute(delete(UploadHistory).where(UploadHistory.video_id == UUID(video_id)))
        
        # 7. Deletar vídeo
        await db.execute(delete(Video).where(Video.id == UUID(video_id)))
        
        await db.commit()
        
        return {
            'success': True,
            'message': 'Video deleted successfully',
            'video_id': video_id
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
