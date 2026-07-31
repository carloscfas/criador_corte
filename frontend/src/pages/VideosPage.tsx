import { useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import api from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Video, ArrowLeft, Trash2 } from 'lucide-react'
import { Video as VideoType } from '@/types'
import { formatDuration } from '@/lib/utils'

export default function VideosPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const { data: videos, isLoading } = useQuery({
    queryKey: ['videos'],
    queryFn: async () => {
      const response = await api.get('/videos/')
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (videoId: string) => {
      await api.delete(`/videos/${videoId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] })
    },
  })

  const handleDeleteVideo = (videoId: string) => {
    if (confirm('Tem certeza que deseja excluir este vídeo e todos os clips associados?')) {
      deleteMutation.mutate(videoId)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center gap-4 mb-8">
        <Button variant="ghost" onClick={() => navigate('/dashboard')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar
        </Button>
        <h1 className="text-3xl font-bold">Vídeos</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos?.map((video: VideoType) => (
          <Card key={video.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Video className="h-4 w-4" />
                {video.original_filename}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Duração: {formatDuration(video.duration || 0)}
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Status: {video.status}
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
