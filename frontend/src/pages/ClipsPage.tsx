import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import api from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Scissors, Download, TrendingUp, ArrowLeft, Loader2 } from 'lucide-react'
import { Clip } from '@/types'
import { formatDuration } from '@/lib/utils'
import { useState } from 'react'

export default function ClipsPage() {
  const navigate = useNavigate()
  const { videoId } = useParams<{ videoId: string }>()
  const [exportingClip, setExportingClip] = useState<string | null>(null)
  
  const { data: clips, isLoading } = useQuery({
    queryKey: ['clips', videoId],
    queryFn: async () => {
      if (!videoId) return null
      const response = await api.get(`/clips/video/${videoId}`)
      return response.data
    },
    enabled: !!videoId
  })

  const exportMutation = useMutation({
    mutationFn: async (clipId: string) => {
      const response = await api.post(`/clips/${clipId}/export`)
      return response.data
    },
    onSuccess: (data) => {
      // Trigger download
      window.open(`/api/clips/download?path=${encodeURIComponent(data.file_path)}`, '_blank')
      setExportingClip(null)
    },
    onError: () => {
      setExportingClip(null)
    }
  })

  const handleExport = (clipId: string) => {
    setExportingClip(clipId)
    exportMutation.mutate(clipId)
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
        <h1 className="text-3xl font-bold">Clips</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {clips?.clips?.map((clip: Clip) => (
          <Card key={clip.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scissors className="h-4 w-4" />
                {clip.title || 'Sem título'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">
                {formatDuration(clip.duration || 0)}
              </p>
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="h-4 w-4 text-primary" />
                <span className="text-2xl font-bold text-primary">
                  {clip.viral_score}
                </span>
              </div>
              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => handleExport(clip.id)}
                  disabled={exportingClip === clip.id}
                >
                  {exportingClip === clip.id ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Exportando...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4 mr-2" />
                      Exportar
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
