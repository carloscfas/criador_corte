import os
from typing import List, Dict, Optional
from datetime import timedelta


class SubtitleService:
    def __init__(self):
        self.output_dir = os.path.join("uploads", "subtitles")
        os.makedirs(self.output_dir, exist_ok=True)

    def format_timestamp(self, seconds: float) -> str:
        """Formata timestamp em formato SRT (00:00:00,000)."""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = td.microseconds // 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def generate_srt(self, segments: List[Dict], output_path: str) -> str:
        """
        Gera legendas em formato SRT.
        
        Args:
            segments: Lista de segments da transcrição
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo gerado
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start = self.format_timestamp(segment['start'])
                end = self.format_timestamp(segment['end'])
                text = segment['text'].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
        
        return output_path

    def generate_word_level_srt(self, segments: List[Dict], output_path: str) -> str:
        """
        Gera legendas em formato SRT com timestamp por palavra (karaokê).
        
        Args:
            segments: Lista de segments com 'words'
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo gerado
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            index = 1
            
            for segment in segments:
                words = segment.get('words', [])
                
                for word_data in words:
                    if 'word' in word_data and 'start' in word_data and 'end' in word_data:
                        start = self.format_timestamp(word_data['start'])
                        end = self.format_timestamp(word_data['end'])
                        word = word_data['word'].strip()
                        
                        f.write(f"{index}\n")
                        f.write(f"{start} --> {end}\n")
                        f.write(f"{word}\n\n")
                        index += 1
        
        return output_path

    def generate_ass(self, segments: List[Dict], output_path: str, style: str = "default") -> str:
        """
        Gera legendas em formato ASS (Advanced Substation Alpha) com suporte a estilos.
        
        Args:
            segments: Lista de segments da transcrição
            output_path: Caminho do arquivo de saída
            style: Estilo da legenda (default, karaoke, highlight)
            
        Returns:
            Caminho do arquivo gerado
        """
        styles = {
            "default": self._get_default_style(),
            "karaoke": self._get_karaoke_style(),
            "highlight": self._get_highlight_style()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header ASS
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\n")
            f.write("WrapStyle: 0\n")
            f.write("ScaledBorderAndShadow: yes\n")
            f.write("YCbCr Matrix: TV.709\n")
            f.write("PlayResX: 1920\n")
            f.write("PlayResY: 1080\n\n")
            
            # Styles
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write(styles[style])
            f.write("\n")
            
            # Events
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            for segment in segments:
                start = self._ass_timestamp(segment['start'])
                end = self._ass_timestamp(segment['end'])
                text = segment['text'].strip().replace('\n', '\\N')
                
                f.write(f"Dialogue: 0,{start},{end},{style},,0,0,0,,{text}\n")
        
        return output_path

    def generate_karaoke_ass(self, segments: List[Dict], output_path: str) -> str:
        """
        Gera legendas em formato ASS com efeito karaokê (palavra por palavra com destaque).
        
        Args:
            segments: Lista de segments com 'words'
            output_path: Caminho do arquivo de saída
            
        Returns:
            Caminho do arquivo gerado
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header ASS
            f.write("[Script Info]\n")
            f.write("ScriptType: v4.00+\n")
            f.write("WrapStyle: 0\n")
            f.write("ScaledBorderAndShadow: yes\n")
            f.write("YCbCr Matrix: TV.709\n")
            f.write("PlayResX: 1920\n")
            f.write("PlayResY: 1080\n\n")
            
            # Styles
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write(self._get_karaoke_style())
            f.write("\n")
            
            # Events
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            for segment in segments:
                words = segment.get('words', [])
                
                for word_data in words:
                    if 'word' in word_data and 'start' in word_data and 'end' in word_data:
                        start = self._ass_timestamp(word_data['start'])
                        end = self._ass_timestamp(word_data['end'])
                        word = word_data['word'].strip()
                        
                        # Efeito karaokê: \k<duration>word
                        duration = int((word_data['end'] - word_data['start']) * 100)
                        f.write(f"Dialogue: 0,{start},{end},Karaoke,,0,0,0,,{{\\k{duration}}}{word}\n")
        
        return output_path

    def _ass_timestamp(self, seconds: float) -> str:
        """Formata timestamp em formato ASS (H:MM:SS.CC)."""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        centiseconds = td.microseconds // 10000
        return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    def _get_default_style(self) -> str:
        """Retorna estilo padrão para ASS."""
        return (
            "Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
            "-1,0,0,0,100,100,0,0,1,3,0,2,10,10,10,1\n"
        )

    def _get_karaoke_style(self) -> str:
        """Retorna estilo karaokê para ASS."""
        return (
            "Style: Karaoke,Arial Bold,56,&H00FFFFFF,&H00FFFF00,&H00000000,&H80000000,"
            "-1,0,0,0,100,100,0,0,1,3,0,2,10,10,10,1\n"
        )

    def _get_highlight_style(self) -> str:
        """Retorna estilo com highlight para ASS."""
        return (
            "Style: Highlight,Arial,52,&H0000FFFF,&H00FF00FF,&H00000000,&H80000000,"
            "-1,0,0,0,100,100,0,0,1,4,0,2,10,10,10,1\n"
        )

    def burn_subtitles_to_video(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        subtitle_format: str = "ass"
    ) -> str:
        """
        Queima (burn) as legendas no vídeo usando FFmpeg.
        
        Args:
            video_path: Caminho do vídeo original
            subtitle_path: Caminho do arquivo de legendas
            output_path: Caminho do vídeo de saída
            subtitle_format: Formato das legendas (srt, ass)
            
        Returns:
            Caminho do vídeo com legendas
        """
        import subprocess
        
        if subtitle_format == "ass":
            # Para ASS, usar filtro ass
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"ass={subtitle_path}",
                "-c:a", "copy",
                "-y",
                output_path
            ]
        else:
            # Para SRT, usar filtro subtitles
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"subtitles={subtitle_path}",
                "-c:a", "copy",
                "-y",
                output_path
            ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"FFmpeg subtitle burning error: {error_msg}")
