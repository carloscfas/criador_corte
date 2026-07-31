import os
import subprocess
import numpy as np
from typing import Optional, List, Tuple
import cv2


class FaceTrackingService:
    def __init__(self):
        self.output_dir = os.path.join("uploads", "processed")
        os.makedirs(self.output_dir, exist_ok=True)

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta faces em um frame usando OpenCV Haar Cascade.
        
        Args:
            frame: Frame do vídeo (numpy array)
            
        Returns:
            Lista de tuplas (x, y, width, height) para cada face detectada
        """
        # Carregar classificador Haar Cascade
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectar faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return [(x, y, w, h) for x, y, w, h in faces]

    def track_speaker(
        self,
        video_path: str,
        output_path: str,
        audio_segments: Optional[List[dict]] = None
    ) -> str:
        """
        Rastreia o falante principal e aplica zoom inteligente.
        
        Args:
            video_path: Caminho do vídeo original
            output_path: Caminho do vídeo processado
            audio_segments: Segmentos de áudio com timestamps (opcional)
            
        Returns:
            Caminho do vídeo processado
        """
        cap = cv2.VideoCapture(video_path)
        
        # Obter propriedades do vídeo
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Configurar writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        last_face_center = None
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detectar faces
            faces = self.detect_faces(frame)
            
            if faces:
                # Usar a maior face (assumindo que é o falante principal)
                largest_face = max(faces, key=lambda f: f[2] * f[3])
                x, y, w, h = largest_face
                
                # Calcular centro da face
                face_center = (x + w // 2, y + h // 2)
                
                # Suavizar movimento (interpolação com frame anterior)
                if last_face_center is not None:
                    alpha = 0.3  # Fator de suavização
                    face_center = (
                        int(alpha * face_center[0] + (1 - alpha) * last_face_center[0]),
                        int(alpha * face_center[1] + (1 - alpha) * last_face_center[1])
                    )
                
                last_face_center = face_center
                
                # Aplicar zoom inteligente (centralizar na face)
                zoom_factor = 1.3
                zoom_width = int(width / zoom_factor)
                zoom_height = int(height / zoom_factor)
                
                # Calcular região de interesse (ROI)
                x1 = max(0, face_center[0] - zoom_width // 2)
                y1 = max(0, face_center[1] - zoom_height // 2)
                x2 = min(width, face_center[0] + zoom_width // 2)
                y2 = min(height, face_center[1] + zoom_height // 2)
                
                # Extrair ROI
                roi = frame[y1:y2, x1:x2]
                
                # Redimensionar para tamanho original
                if roi.size > 0:
                    frame = cv2.resize(roi, (width, height))
            
            out.write(frame)
            frame_count += 1
            
            # Progresso
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}%")
        
        cap.release()
        out.release()
        
        return output_path

    def apply_smart_crop(
        self,
        video_path: str,
        output_path: str,
        target_aspect_ratio: str = "9:16"
    ) -> str:
        """
        Aplica crop inteligente para formato vertical (9:16).
        
        Args:
            video_path: Caminho do vídeo original
            output_path: Caminho do vídeo processado
            target_aspect_ratio: Razão de aspecto alvo (9:16 para Shorts)
            
        Returns:
            Caminho do vídeo processado
        """
        # Usar FFmpeg para crop inteligente
        if target_aspect_ratio == "9:16":
            # Para 9:16, centralizar e cropar
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0",
                "-c:a", "copy",
                "-y",
                output_path
            ]
        else:
            # Crop padrão
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"crop={target_aspect_ratio}",
                "-c:a", "copy",
                "-y",
                output_path
            ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"FFmpeg smart crop error: {error_msg}")

    def detect_scene_changes(self, video_path: str, threshold: float = 0.3) -> List[float]:
        """
        Detecta mudanças de cena no vídeo.
        
        Args:
            video_path: Caminho do vídeo
            threshold: Limiar para detecção de mudança (0-1)
            
        Returns:
            Lista de timestamps onde ocorrem mudanças de cena
        """
        cap = cv2.VideoCapture(video_path)
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        scene_changes = []
        
        prev_frame = None
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Converter para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calcular diferença entre frames
                diff = cv2.absdiff(prev_frame, gray)
                diff_score = np.mean(diff) / 255.0
                
                # Se diferença acima do limiar, é uma mudança de cena
                if diff_score > threshold:
                    timestamp = frame_count / fps
                    scene_changes.append(timestamp)
            
            prev_frame = gray
            frame_count += 1
        
        cap.release()
        
        return scene_changes
