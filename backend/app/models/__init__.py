# Importar todos os models para garantir que sejam carregados pelo SQLAlchemy
from app.models.user import User
from app.models.project import Project
from app.models.video import Video
from app.models.audio_file import AudioFile
from app.models.transcription import Transcription
from app.models.clip import Clip
from app.models.ai_analysis import AIAnalysis
from app.models.export_job import ExportJob
from app.models.upload_history import UploadHistory

__all__ = [
    "User",
    "Project", 
    "Video",
    "AudioFile",
    "Transcription",
    "Clip",
    "AIAnalysis",
    "ExportJob",
    "UploadHistory"
]
