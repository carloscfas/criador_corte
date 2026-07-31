from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from uuid import UUID


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)

    async def create_project(self, user_id: UUID, project_data: ProjectCreate) -> ProjectResponse:
        project = Project(
            name=project_data.name,
            description=project_data.description,
            user_id=user_id
        )
        created_project = await self.project_repo.create(project)
        return ProjectResponse.model_validate(created_project)

    async def get_project(self, project_id: str, user_id: str) -> ProjectResponse:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        if str(project.user_id) != user_id:
            raise ValueError("Access denied")
        return ProjectResponse.model_validate(project)

    async def get_user_projects(self, user_id: UUID) -> List[ProjectResponse]:
        projects = await self.project_repo.get_by_user(user_id)
        return [ProjectResponse.model_validate(p) for p in projects]

    async def update_project(self, project_id: UUID, user_id: UUID, project_data: ProjectUpdate) -> ProjectResponse:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        if project.user_id != user_id:
            raise ValueError("Access denied")

        if project_data.name is not None:
            project.name = project_data.name
        if project_data.description is not None:
            project.description = project_data.description

        updated_project = await self.project_repo.update(project)
        return ProjectResponse.model_validate(updated_project)

    async def delete_project(self, project_id: UUID, user_id: UUID) -> bool:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")
        if project.user_id != user_id:
            raise ValueError("Access denied")

        return await self.project_repo.delete(project_id)
