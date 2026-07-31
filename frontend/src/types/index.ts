export interface User {
  id: string
  email: string
  full_name?: string
  is_active: boolean
  created_at: string
}

export interface Project {
  id: string
  name: string
  description?: string
  user_id: string
  created_at: string
  updated_at: string
}

export interface Video {
  id: string
  project_id: string
  original_filename: string
  file_path: string
  file_size?: number
  duration?: number
  status: 'uploaded' | 'processing' | 'transcribing' | 'analyzing' | 'completed' | 'failed'
  language?: string
  created_at: string
}

export interface Clip {
  id: string
  video_id: string
  title?: string
  description?: string
  start_time: number
  end_time: number
  duration?: number
  viral_score?: number
  category?: string
  tags?: string[]
  is_approved: boolean
  file_path?: string
  thumbnail_path?: string
  created_at: string
}

export interface DashboardStats {
  total_videos: number
  total_clips: number
  total_projects: number
  total_duration_processed: number
  average_viral_score?: number
  time_saved: number
  videos_by_status: Record<string, number>
  clips_by_category: Record<string, number>
}

export interface DashboardData {
  stats: DashboardStats
  recent_videos: Video[]
  top_clips: Clip[]
}
