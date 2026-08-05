from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.videos import router as videos_router
from app.api.status import router as status_router
from app.api.clips import router as clips_router
from app.api.dashboard import router as dashboard_router
from app.api.export import router as export_router
from app.api.social import router as social_router

app = FastAPI(
    title="Criador de Cortes API",
    description="API para geração automática de Shorts de vídeos longos",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(videos_router)
app.include_router(status_router)
app.include_router(clips_router)
app.include_router(dashboard_router)
app.include_router(export_router)
app.include_router(social_router)


@app.get("/")
async def root():
    return {"message": "Criador de Cortes API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
