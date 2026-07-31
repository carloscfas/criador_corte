import os
import subprocess
import uuid
from typing import Optional
from app.core.config import settings


class VideoExportService:
    def __init__(self):
        self.output_dir = os.path.join(settings.UPLOAD_DIR, "exports")
        os.makedirs(self.output_dir, exist_ok=True)

    def export_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_path: Optional[str] = None,
        resolution: str = "1080x1920",
        fps: int = 60,
        format: str = "mp4",
        add_subtitles: bool = False,
        subtitle_path: Optional[str] = None
    ) -> str:
        """
        Exporta um clip do vídeo original.
        
        Args:
            video_path: Caminho do vídeo original
            start_time: Tempo de início em segundos
            end_time: Tempo de fim em segundos
            output_path: Caminho de saída (opcional)
            resolution: Resolução (ex: 1080x1920 para 9:16)
            fps: Frames por segundo
            format: Formato de saída (mp4)
            add_subtitles: Se deve adicionar legendas
            subtitle_path: Caminho do arquivo de legendas
            
        Returns:
            Caminho do vídeo exportado
        """
        if output_path is None:
            output_path = os.path.join(self.output_dir, f"{uuid.uuid4()}.{format}")

        duration = end_time - start_time

        # Comando FFmpeg para cortar e redimensionar
        cmd = [
            "ffmpeg",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(duration),
            "-vf", f"scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-r", str(fps),
            "-movflags", "+faststart",
            "-y",
            output_path
        ]

        # Adicionar legendas se solicitado
        if add_subtitles and subtitle_path:
            if subtitle_path.endswith('.ass'):
                cmd = [
                    "ffmpeg",
                    "-ss", str(start_time),
                    "-i", video_path,
                    "-vf", f"ass={subtitle_path},scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-r", str(fps),
                    "-movflags", "+faststart",
                    "-y",
                    output_path
                ]
            else:  # SRT
                cmd = [
                    "ffmpeg",
                    "-ss", str(start_time),
                    "-i", video_path,
                    "-vf", f"subtitles={subtitle_path},scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2",
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-r", str(fps),
                    "-movflags", "+faststart",
                    "-y",
                    output_path
                ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"FFmpeg export error: {error_msg}")

    def generate_thumbnail(
        self,
        video_path: str,
        timestamp: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Gera um thumbnail do vídeo em um timestamp específico.
        
        Args:
            video_path: Caminho do vídeo
            timestamp: Timestamp em segundos
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do thumbnail gerado
        """
        if output_path is None:
            output_path = os.path.join(self.output_dir, f"thumb_{uuid.uuid4()}.jpg")

        cmd = [
            "ffmpeg",
            "-ss", str(timestamp),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            "-y",
            output_path
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"FFmpeg thumbnail error: {error_msg}")

    def get_video_info(self, video_path: str) -> dict:
        """
        Obtém informações do vídeo usando FFprobe.
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Dicionário com informações do vídeo
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration,codec_name",
            "-show_entries", "format=duration",
            "-of", "json",
            video_path
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
            import json
            info = json.loads(result.stdout)
            
            stream = info.get("streams", [{}])[0]
            format_info = info.get("format", {})
            
            return {
                "width": stream.get("width"),
                "height": stream.get("height"),
                "duration": float(format_info.get("duration", stream.get("duration", 0))),
                "codec": stream.get("codec_name")
            }
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            raise Exception(f"FFprobe error: {str(e)}")
