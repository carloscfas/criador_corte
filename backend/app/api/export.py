from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.export import ExportRequest, ExportResponse, ExportJobResponse
from app.services.export_service import ExportService
from app.core.deps import get_current_user_id

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def create_export(
    export_request: ExportRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Cria um novo job de exportação."""
    try:
        export_service = ExportService(db)
        return await export_service.create_export_job(user_id, export_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/job/{job_id}", response_model=ExportJobResponse)
async def get_export_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Retorna o status de um job de exportação."""
    try:
        export_service = ExportService(db)
        return await export_service.get_export_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/clip/{clip_id}", response_model=List[ExportJobResponse])
async def get_clip_exports(
    clip_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Retorna todos os jobs de exportação de um clip."""
    from uuid import UUID
    export_service = ExportService(db)
    return await export_service.get_clip_exports(UUID(clip_id))
