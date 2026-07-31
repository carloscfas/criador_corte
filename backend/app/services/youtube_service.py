import os
import yt_dlp
from typing import Optional
from pathlib import Path


class YouTubeService:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        Path(upload_dir).mkdir(parents=True, exist_ok=True)

    def _detect_platform(self, url: str) -> str:
        """Detecta a plataforma da URL (youtube, instagram, tiktok)"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'tiktok.com' in url:
            return 'tiktok'
        else:
            return 'unknown'

    def download_video(self, url: str, project_id: str) -> dict:
        """
        Baixa um vídeo de YouTube, Instagram ou TikTok e retorna informações sobre o arquivo baixado.
        
        Args:
            url: URL do vídeo (YouTube, Instagram ou TikTok)
            project_id: ID do projeto para organizar os arquivos
            
        Returns:
            dict com informações do vídeo baixado
        """
        platform = self._detect_platform(url)
        print(f"Detected platform: {platform}")
        
        project_dir = os.path.join(self.upload_dir, project_id)
        Path(project_dir).mkdir(parents=True, exist_ok=True)
        
        output_template = os.path.join(project_dir, "%(title)s.%(ext)s")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/bestvideo+bestaudio/best',
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        
        # Opções específicas por plataforma
        if platform == 'instagram':
            ydl_opts.update({
                'format': 'best',
            })
        elif platform == 'tiktok':
            ydl_opts.update({
                'format': 'best',
            })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Primeiro obter informações
                print(f"Extracting info from URL: {url}")
                info = ydl.extract_info(url, download=False)
                print(f"Video info: {info.get('title')}")
                
                # Baixar o vídeo
                print(f"Starting download...")
                ydl.download([url])
                print(f"Download completed")
                
                # Encontrar o arquivo baixado
                filename = ydl.prepare_filename(info)
                
                # Verificar se o arquivo existe
                if not os.path.exists(filename):
                    # Tentar encontrar arquivo .mp4 no diretório
                    mp4_files = list(Path(project_dir).glob("*.mp4"))
                    if mp4_files:
                        filename = str(mp4_files[0])
                    else:
                        raise Exception(f"Downloaded file not found at {filename}")
                
                return {
                    'success': True,
                    'filename': os.path.basename(filename),
                    'filepath': filename,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                    'uploader': info.get('uploader'),
                    'platform': platform
                }
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }

    def get_video_info(self, url: str) -> dict:
        """
        Obtém informações sobre um vídeo do YouTube sem baixar.
        
        Args:
            url: URL do YouTube
            
        Returns:
            dict com informações do vídeo
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'success': True,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                    'upload_date': info.get('upload_date'),
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
