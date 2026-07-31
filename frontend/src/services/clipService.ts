import api from '@/lib/api'
import { Clip } from '@/types'

export interface UpdateClipData {
  title?: string
  description?: string
  tags?: string[]
}

export const clipService = {
  async getClipsByVideo(videoId: string): Promise<Clip[]> {
    const response = await api.get(`/clips/video/${videoId}`)
    return response.data
  },

  async getClip(id: string): Promise<Clip> {
    const response = await api.get(`/clips/${id}`)
    return response.data
  },

  async updateClip(id: string, data: UpdateClipData): Promise<Clip> {
    const response = await api.put(`/clips/${id}`, data)
    return response.data
  },

  async approveClip(id: string): Promise<Clip> {
    const response = await api.post(`/clips/${id}/approve`)
    return response.data
  }
}
