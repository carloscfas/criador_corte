from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi.responses import FileResponse
from app.database import get_db
from app.schemas.clip import ClipResponse, ClipUpdate, ClipListResponse
from app.repositories.clip_repository import ClipRepository
from app.core.deps import get_current_user_id

router = APIRouter(prefix="/api/clips", tags=["clips"])


@router.get("/video/{video_id}", response_model=ClipListResponse)
async def get_video_clips(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retorna todos os clips de um vídeo, ordenados por score de viralização."""
    clip_repo = ClipRepository(db)
    clips = await clip_repo.get_by_video(video_id)
    
    return ClipListResponse(
        clips=[ClipResponse.model_validate(clip) for clip in clips],
        total=len(clips)
    )


@router.get("/{clip_id}", response_model=ClipResponse)
async def get_clip(
    clip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retorna detalhes de um clip específico."""
    clip_repo = ClipRepository(db)
    clip = await clip_repo.get_by_id(clip_id)
    
    if not clip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip not found")
    
    return ClipResponse.model_validate(clip)


@router.put("/{clip_id}", response_model=ClipResponse)
async def update_clip(
    clip_id: str,
    clip_data: ClipUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Atualiza um clip (título, descrição, aprovação)."""
    clip_repo = ClipRepository(db)
    clip = await clip_repo.get_by_id(clip_id)
    
    if not clip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip not found")
    
    if clip_data.title is not None:
        clip.title = clip_data.title
    if clip_data.description is not None:
        clip.description = clip_data.description
    if clip_data.is_approved is not None:
        clip.is_approved = clip_data.is_approved
    
    updated_clip = await clip_repo.update(clip)
    return ClipResponse.model_validate(updated_clip)


@router.post("/{clip_id}/approve", response_model=ClipResponse)
async def approve_clip(
    clip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Aprova um clip para exportação."""
    clip_repo = ClipRepository(db)
    approved_clip = await clip_repo.approve(clip_id)
    
    if not approved_clip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip not found")
    
    return ClipResponse.model_validate(approved_clip)


@router.post("/{clip_id}/export")
async def export_clip(
    clip_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Exporta um clip usando FFmpeg."""
    from app.repositories.clip_repository import ClipRepository
    from app.repositories.video_repository import VideoRepository
    import subprocess
    import os
    from app.core.config import settings
    
    clip_repo = ClipRepository(db)
    video_repo = VideoRepository(db)
    
    clip = await clip_repo.get_by_id(clip_id)
    if not clip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip not found")
    
    video = await video_repo.get_by_id(clip.video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    
    # Criar diretório de exportação se não existir
    export_dir = os.path.join(settings.UPLOAD_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    # Caminho do arquivo de exportação
    output_path = os.path.join(export_dir, f"clip_{clip.id}.mp4")
    
    # Usar FFmpeg para extrair o clip do vídeo original
    try:
        cmd = [
            "ffmpeg",
            "-i", video.file_path,
            "-ss", str(clip.start_time),
            "-t", str(clip.duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",  # Sobrescrever se existir
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Atualizar o clip com o caminho do arquivo exportado
        clip.file_path = output_path
        await clip_repo.update(clip)
        
        return {
            "success": True,
            "message": "Clip exported successfully",
            "file_path": output_path
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export error: {str(e)}"
        )


@router.get("/download")
async def download_file(path: str):
    """Download a file from the uploads directory."""
    import os
    from app.core.config import settings
    
    # Security: ensure the path is within the uploads directory
    if not path.startswith(settings.UPLOAD_DIR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: path outside uploads directory"
        )
    
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path,
        media_type='video/mp4',
        filename=os.path.basename(path)
    )
