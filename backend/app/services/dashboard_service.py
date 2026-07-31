from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.video import Video, VideoStatus
from app.models.clip import Clip
from app.models.project import Project
from app.schemas.dashboard import DashboardStats, DashboardResponse
from uuid import UUID


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self, user_id: UUID) -> DashboardStats:
        """
        Calcula estatísticas do dashboard para um usuário.
        """
        # Total de vídeos
        videos_result = await self.db.execute(
            select(func.count(Video.id))
            .join(Project, Video.project_id == Project.id)
            .where(Project.user_id == user_id)
        )
        total_videos = videos_result.scalar() or 0

        # Total de clips
        clips_result = await self.db.execute(
            select(func.count(Clip.id))
            .join(Video, Clip.video_id == Video.id)
            .join(Project, Video.project_id == Project.id)
            .where(Project.user_id == user_id)
        )
        total_clips = clips_result.scalar() or 0

        # Total de projetos
        projects_result = await self.db.execute(
            select(func.count(Project.id))
            .where(Project.user_id == user_id)
        )
        total_projects = projects_result.scalar() or 0

        # Tempo total processado (soma de durações dos vídeos)
        duration_result = await self.db.execute(
            select(func.sum(Video.duration))
            .join(Project, Video.project_id == Project.id)
            .where(Project.user_id == user_id)
        )
        total_duration_processed = duration_result.scalar() or 0

        # Score médio de viralização
        score_result = await self.db.execute(
            select(func.avg(Clip.viral_score))
            .join(Video, Clip.video_id == Video.id)
            .join(Project, Video.project_id == Project.id)
            .where(Project.user_id == user_id)
            .where(Clip.viral_score.isnot(None))
        )
        average_viral_score = score_result.scalar()

        # Vídeos por status
        status_result = await self.db.execute(
            select(Video.status, func.count(Video.id))
            .join(Project, Video.project_id == Project.id)
            .where(Project.user_id == user_id)
            .group_by(Video.status)
        )
        videos_by_status = {status.value: count for status, count in status_result.all()}

        # Clips por categoria
        category_result = await self.db.execute(
            select(Clip.category, func.count(Clip.id))
            .join(Video, Clip.video_id == Video.id)
            .join(Project, Video.project_id == Project.id)
            .where(Project.user_id == user_id)
            .where(Clip.category.isnot(None))
            .group_by(Clip.category)
        )
        clips_by_category = {category: count for category, count in category_result.all()}

        # Tempo economizado (estimativa: 1 hora de edição manual por clip)
        time_saved = total_clips * 3600  # 1 hora = 3600 segundos

        return DashboardStats(
            total_videos=total_videos,
            total_clips=total_clips,
            total_projects=total_projects,
            total_duration_processed=total_duration_processed,
            average_viral_score=average_viral_score,
            time_saved=time_saved,
            videos_by_status=videos_by_status,
            clips_by_category=clips_by_category
        )

    async def get_recent_videos(self, user_id: UUID, limit: int = 5) -> list:
        """
        Retorna os vídeos mais recentes do usuário.
        """
        from app.schemas.video import VideoResponse
        
        result = await self.db.execute(
            select(Video)
            .join(Project, Video.project_id == Project.id)
            .where(Project.user_id == user_id)
            .order_by(Video.created_at.desc())
            .limit(limit)
        )
        videos = result.scalars().all()
        return [VideoResponse.model_validate(video) for video in videos]

    async def get_top_clips(self, user_id: UUID, limit: int = 5) -> list:
        """
        Retorna os clips com maior score de viralização.
        """
        from app.schemas.clip import ClipResponse
        
        result = await self.db.execute(
            select(Clip)
            .join(Video, Clip.video_id == Video.id)
            .join(Project, Video.project_id == Project.id)
            .where(Project.user_id == user_id)
            .where(Clip.viral_score.isnot(None))
            .order_by(Clip.viral_score.desc())
            .limit(limit)
        )
        clips = result.scalars().all()
        return [ClipResponse.model_validate(clip) for clip in clips]

    async def get_dashboard(self, user_id: UUID) -> DashboardResponse:
        """
        Retorna dados completos do dashboard.
        """
        stats = await self.get_dashboard_stats(user_id)
        recent_videos = await self.get_recent_videos(user_id)
        top_clips = await self.get_top_clips(user_id)

        return DashboardResponse(
            stats=stats,
            recent_videos=recent_videos,
            top_clips=top_clips
        )
