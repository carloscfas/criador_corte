import { useParams, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import api from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Upload, Video, Youtube, ArrowLeft, Trash2, Download } from 'lucide-react'
import { formatDuration } from '@/lib/utils'

export default function ProjectDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [file, setFile] = useState<File | null>(null)
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [uploading, setUploading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [uploadType, setUploadType] = useState<'file' | 'youtube'>('file')

  const { data: project } = useQuery({
    queryKey: ['project', id],
    queryFn: async () => {
      const response = await api.get(`/projects/${id}`)
      return response.data
    },
  })

  const { data: videos } = useQuery({
    queryKey: ['videos', id],
    queryFn: async () => {
      const response = await api.get(`/videos/project/${id}`)
      return response.data
    },
  })

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      await api.post(`/videos/upload/${id}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      queryClient.invalidateQueries({ queryKey: ['videos', id] })
      setFile(null)
    } catch (error) {
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleYouTubeDownload = async () => {
    if (!youtubeUrl) return

    setDownloading(true)
    try {
      await api.post(`/videos/youtube/${id}`, { url: youtubeUrl })
      queryClient.invalidateQueries({ queryKey: ['videos', id] })
      setYoutubeUrl('')
    } catch (error) {
      console.error('YouTube download error:', error)
    } finally {
      setDownloading(false)
    }
  }

  const deleteMutation = useMutation({
    mutationFn: async (videoId: string) => {
      await api.delete(`/videos/${videoId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos', id] })
    },
  })

  const handleDeleteVideo = (videoId: string) => {
    if (confirm('Tem certeza que deseja excluir este vídeo e todos os clips associados?')) {
      deleteMutation.mutate(videoId)
    }
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/projects')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
          <h1 className="text-3xl font-bold">{project?.name}</h1>
        </div>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Download de Vídeos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <Button
              variant={uploadType === 'file' ? 'default' : 'outline'}
              onClick={() => setUploadType('file')}
            >
              <Upload className="h-4 w-4 mr-2" />
              Arquivo
            </Button>
            <Button
              variant={uploadType === 'youtube' ? 'default' : 'outline'}
              onClick={() => setUploadType('youtube')}
            >
              <Download className="h-4 w-4 mr-2" />
              URL (YouTube/Instagram/TikTok)
            </Button>
          </div>

          {uploadType === 'file' ? (
            <div className="flex gap-4">
              <Input
                type="file"
                accept="video/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <Button onClick={handleUpload} disabled={!file || uploading}>
                <Upload className="h-4 w-4 mr-2" />
                {uploading ? 'Enviando...' : 'Upload'}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <Label htmlFor="video-url">URL do Vídeo</Label>
                <Input
                  id="video-url"
                  placeholder="https://www.youtube.com/watch?v=... ou https://www.instagram.com/... ou https://www.tiktok.com/..."
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                />
              </div>
              <Button 
                onClick={handleYouTubeDownload} 
                disabled={!youtubeUrl || downloading}
                className="w-full"
              >
                <Download className="h-4 w-4 mr-2" />
                {downloading ? 'Baixando...' : 'Baixar Vídeo'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <h2 className="text-2xl font-bold mb-4">Vídeos Baixados</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos?.map((video: any) => (
          <Card key={video.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="h-4 w-4" />
                {video.original_filename}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Duração: {formatDuration(video.duration || 0)}
              </p>
              <Button 
                size="sm" 
                variant="destructive"
                className="w-full"
                onClick={() => handleDeleteVideo(video.id)}
                disabled={deleteMutation.isPending}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Excluir
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
