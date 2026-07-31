import api from '@/lib/api'
import { Video } from '@/types'

export interface UploadVideoData {
  project_id: string
  file: File
}

export const videoService = {
  async uploadVideo(projectId: string, file: File, onProgress?: (progress: number) => void): Promise<Video> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(`/videos/upload/${projectId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })

    return response.data
  },

  async getVideo(id: string): Promise<Video> {
    const response = await api.get(`/videos/${id}`)
    return response.data
  },

  async getVideoStatus(id: string): Promise<{ status: string; progress?: number }> {
    const response = await api.get(`/status/video/${id}`)
    return response.data
  }
}
