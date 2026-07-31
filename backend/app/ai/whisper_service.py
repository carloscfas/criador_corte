import os
from typing import Optional, Dict, List
try:
    import whisper
except ImportError:
    from openai import whisper
from app.core.config import settings


class WhisperService:
    def __init__(self, model_size: str = "tiny"):
        """
        Inicializa o serviço de transcrição Whisper.
        
        Args:
            model_size: Tamanho do modelo (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        # Carregar modelo apenas quando necessário para economizar memória
        self._load_model()

    def _load_model(self):
        """Carrega o modelo Whisper (lazy loading)."""
        if self.model is None:
            self.model = whisper.load_model(self.model_size)

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcreve o áudio usando Whisper.
        
        Args:
            audio_path: Caminho do arquivo de áudio
            language: Código do idioma (pt, en, es, etc). Se None, detecta automaticamente
            task: 'transcribe' ou 'translate'
            
        Returns:
            Dicionário com:
            - text: texto completo
            - segments: lista de segmentos com timestamps
            - language: idioma detectado
        """
        self._load_model()
        
        # Opções de transcrição otimizadas para velocidade
        options = {
            "task": task,
            "word_timestamps": False,  # Desabilitado para velocidade
            "fp16": False,  # Usar FP32 para maior compatibilidade
            "compression_ratio_threshold": 2.4,  # Mais agressivo para descartar silêncio
            "no_speech_threshold": 0.6,  # Threshold mais alto para ignorar silêncio
            "condition_on_previous_text": False,  # Não depender do texto anterior
        }
        
        if language:
            options["language"] = language
        
        try:
            # Transcrever o áudio completo (removido limite de 10 minutos)
            result = self.model.transcribe(audio_path, **options)
            
            # Formatar resultado
            formatted_segments = []
            for segment in result["segments"]:
                formatted_segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                    "confidence": segment.get("avg_logprob", 0.0),
                    "words": segment.get("words", [])
                })
            
            return {
                "text": result["text"].strip(),
                "segments": formatted_segments,
                "language": result["language"],
                "duration": sum(seg["end"] - seg["start"] for seg in formatted_segments)
            }
            
        except Exception as e:
            raise Exception(f"Whisper transcription error: {str(e)}")

    def detect_language(self, audio_path: str) -> str:
        """
        Detecta o idioma do áudio.
        """
        self._load_model()
        
        # Carregar apenas o áudio para detecção
        audio = whisper.load_audio(audio_path)
        
        # Detectar idioma
        audio_tensor = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio_tensor).to(self.model.device)
        _, probs = self.model.detect_language(mel)
        
        # Retornar o idioma com maior probabilidade
        detected_lang = max(probs, key=probs.get)
        return detected_lang
