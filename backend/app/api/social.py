from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.ai.social_media_service import SocialMediaService, SocialPlatform
from app.core.deps import get_current_user_id
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/social", tags=["social"])


class PublishRequest(BaseModel):
    clip_id: str
    platforms: List[str]
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class PublishResponse(BaseModel):
    platform: str
    status: str
    video_id: Optional[str]
    url: Optional[str]
    message: str


@router.post("/publish", response_model=dict)
async def publish_to_social(
    request: PublishRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Publica um clip em redes sociais.
    Nota: Requer configuração das APIs das plataformas.
    """
    # TODO: Obter clip do banco e validar permissões
    # TODO: Obter caminho do vídeo exportado
    
    social_service = SocialMediaService()
    
    # Converter nomes de plataformas para enum
    platform_map = {
        "youtube": SocialPlatform.YOUTUBE,
        "tiktok": SocialPlatform.TIKTOK,
        "instagram": SocialPlatform.INSTAGRAM
    }
    
    platforms = [platform_map[p] for p in request.platforms if p in platform_map]
    
    # Placeholder - em produção, usar caminho real do vídeo
    video_path = "uploads/exports/placeholder.mp4"
    
    result = await social_service.publish_to_all(
        video_path=video_path,
        title=request.title or "Título padrão",
        description=request.description or "Descrição padrão",
        tags=request.tags or [],
        platforms=platforms
    )
    
    return result


@router.get("/requirements")
async def get_publishing_requirements():
    """
    Retorna os requisitos para publicação em cada plataforma.
    """
    social_service = SocialMediaService()
    return social_service.get_publishing_requirements()
