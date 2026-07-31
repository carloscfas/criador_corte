from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.video_repository import VideoRepository
from app.core.deps import get_current_user_id

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/video/{video_id}")
async def get_video_status(
    video_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Retorna o status atual de processamento de um vídeo."""
    video_repo = VideoRepository(db)
    video = await video_repo.get_by_id(video_id)
    
    if not video:
        return {"error": "Video not found"}
    
    return {
        "video_id": video.id,
        "status": video.status.value,
        "duration": video.duration,
        "language": video.language
    }
