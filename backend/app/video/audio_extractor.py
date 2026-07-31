import os
import subprocess
import uuid
from typing import Optional
from app.core.config import settings


class AudioExtractor:
    def __init__(self):
        self.output_dir = os.path.join(settings.UPLOAD_DIR, "audio")
        os.makedirs(self.output_dir, exist_ok=True)

    def extract(self, video_path: str, output_format: str = "mp3") -> str:
        """
        Extrai áudio do vídeo usando FFmpeg.
        
        Args:
            video_path: Caminho do arquivo de vídeo
            output_format: Formato de saída (mp3, wav, etc)
            
        Returns:
            Caminho do arquivo de áudio extraído
        """
        # Gerar nome único para o arquivo de áudio
        audio_id = str(uuid.uuid4())
        audio_path = os.path.join(self.output_dir, f"{audio_id}.{output_format}")
        
        # Comando FFmpeg para extrair áudio
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # No video
            "-acodec", "libmp3lame" if output_format == "mp3" else "pcm_s16le",
            "-ab", "192k",  # Bitrate
            "-ar", "16000",  # Sample rate (16kHz é ideal para Whisper)
            "-y",  # Sobrescrever se existir
            audio_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            
            # Obter duração do áudio
            duration = self._get_audio_duration(audio_path)
            
            return {
                "path": audio_path,
                "format": output_format,
                "sample_rate": 16000,
                "duration": duration
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"FFmpeg error: {error_msg}")

    def _get_audio_duration(self, audio_path: str) -> Optional[float]:
        """
        Obtém a duração do áudio usando FFprobe.
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            duration = float(result.stdout.strip())
            return duration
        except (subprocess.CalledProcessError, ValueError):
            return None
