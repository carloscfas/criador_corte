from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService
from app.core.deps import get_current_user_id

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Retorna dados completos do dashboard do usuário."""
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_dashboard(user_id)
