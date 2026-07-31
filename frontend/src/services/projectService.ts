import api from '@/lib/api'
import { Project } from '@/types'

export interface CreateProjectData {
  name: string
  description?: string
}

export interface UpdateProjectData {
  name?: string
  description?: string
}

export const projectService = {
  async getProjects(): Promise<Project[]> {
    const response = await api.get('/projects/')
    return response.data
  },

  async getProject(id: string): Promise<Project> {
    const response = await api.get(`/projects/${id}`)
    return response.data
  },

  async createProject(data: CreateProjectData): Promise<Project> {
    const response = await api.post('/projects/', data)
    return response.data
  },

  async updateProject(id: string, data: UpdateProjectData): Promise<Project> {
    const response = await api.put(`/projects/${id}`, data)
    return response.data
  },

  async deleteProject(id: string): Promise<void> {
    await api.delete(`/projects/${id}`)
  }
}
