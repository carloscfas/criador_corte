from pydantic import BaseModel
from typing import Optional


class DashboardStats(BaseModel):
    total_videos: int
    total_clips: int
    total_projects: int
    total_duration_processed: float  # em segundos
    average_viral_score: Optional[float]
    time_saved: float  # tempo economizado em segundos (estimativa)
    videos_by_status: dict
    clips_by_category: dict


class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_videos: list
    top_clips: list
