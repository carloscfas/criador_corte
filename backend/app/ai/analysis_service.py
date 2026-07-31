from typing import Dict, List, Optional
import google.generativeai as genai
from app.core.config import settings


class AnalysisService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    async def analyze(self, transcription: Dict) -> Dict:
        """
        Analisa a transcrição para encontrar os melhores momentos.

        Args:
            transcription: Dicionário com 'text' e 'segments' da transcrição

        Returns:
            Dicionário com análise completa
        """
        if not self.model:
            raise Exception("Gemini API key not configured")

        text = transcription["text"]
        segments = transcription["segments"]

        # Prompt para análise
        prompt = self._build_analysis_prompt(text)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    response_mime_type="application/json"
                )
            )

            analysis = self._parse_analysis_response(response.text)

            # Adicionar timestamps baseados nos segments
            analysis = self._enrich_with_timestamps(analysis, segments)

            return analysis

        except Exception as e:
            raise Exception(f"Gemini analysis error: {str(e)}")

    def _build_analysis_prompt(self, text: str) -> str:
        """Constrói o prompt para análise."""
        return f"""
Analise a seguinte transcrição e identifique:

1. **Histórias**: Narrativas completas com início, meio e fim
2. **Piadas**: Momentos de humor que podem gerar risadas
3. **Polêmicas**: Assuntos controversos ou opiniões fortes
4. **Emoções**: Momentos de alta carga emocional (alegria, tristeza, raiva, surpresa)
5. **Curiosidades**: Fatos interessantes ou pouco conhecidos
6. **Frases impactantes**: Citações memoráveis ou ensinamentos
7. **Ensinos**: Lições práticas ou conselhos valiosos
8. **Momentos engraçados**: Situações cômicas ou anedotas
9. **Momentos emocionantes**: Trechos que tocam o coração

Para cada momento identificado, forneça:
- Tipo (história, piada, polêmica, etc)
- Resumo breve (1-2 frases)
- Texto exato do momento
- Score de viralização (0-100)

Transcrição:
{text}

Responda em JSON com esta estrutura:
{{
    "summary": "Resumo geral do conteúdo em 2-3 frases",
    "key_topics": ["tópico1", "tópico2", "tópico3"],
    "emotions_detected": [
        {{"emotion": "nome_da_emoção", "confidence": 0.0-1.0}}
    ],
    "stories": [
        {{"summary": "resumo", "text": "texto", "score": 0-100}}
    ],
    "jokes": [
        {{"text": "texto", "score": 0-100}}
    ],
    "controversies": [
        {{"topic": "tópico", "text": "texto", "score": 0-100}}
    ],
    "teachings": [
        {{"lesson": "lição", "text": "texto", "score": 0-100}}
    ],
    "viral_moments": [
        {{"type": "tipo", "text": "texto", "score": 0-100, "reason": "motivo"}}
    ]
}}
"""

    def _parse_analysis_response(self, response: str) -> Dict:
        """Parseia a resposta da OpenAI."""
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse OpenAI response: {str(e)}")

    def _enrich_with_timestamps(self, analysis: Dict, segments: List[Dict]) -> Dict:
        """
        Enriquece a análise com timestamps baseados nos segments.
        Usa busca de texto aproximada com múltiplas estratégias para encontrar onde cada momento ocorre.
        """
        def find_timestamp(text: str, segments: List[Dict]) -> tuple:
            """Encontra o timestamp aproximado de um texto usando múltiplas estratégias."""
            import re
            
            # Normalizar texto para busca
            search_text = text.lower().strip()
            # Remover pontuação para melhor matching
            search_text_clean = re.sub(r'[^\w\s]', '', search_text)
            
            # Estratégia 1: Buscar substring exata (primeiros 100 chars)
            for length in [100, 75, 50, 30]:
                if len(search_text) >= length:
                    substring = search_text[:length]
                    for segment in segments:
                        if substring in segment["text"].lower():
                            return segment["start"], segment["end"]
            
            # Estratégia 2: Buscar palavras-chave (3+ palavras consecutivas)
            words = search_text_clean.split()
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                if len(phrase) >= 10:  # Mínimo 10 caracteres
                    for segment in segments:
                        segment_clean = re.sub(r'[^\w\s]', '', segment["text"].lower())
                        if phrase in segment_clean:
                            return segment["start"], segment["end"]
            
            # Estratégia 3: Buscar qualquer palavra longa (>5 chars) do texto
            long_words = [w for w in words if len(w) > 5]
            for word in long_words[:3]:  # Tentar as 3 primeiras palavras longas
                for segment in segments:
                    if word in segment["text"].lower():
                        return segment["start"], segment["end"]
            
            return None, None

        # Enrich stories
        for story in analysis.get("stories", []):
            start, end = find_timestamp(story["text"], segments)
            story["start"] = start
            story["end"] = end

        # Enrich jokes
        for joke in analysis.get("jokes", []):
            start, end = find_timestamp(joke["text"], segments)
            joke["start"] = start
            joke["end"] = end

        # Enrich controversies
        for controversy in analysis.get("controversies", []):
            start, end = find_timestamp(controversy["text"], segments)
            controversy["start"] = start
            controversy["end"] = end

        # Enrich teachings
        for teaching in analysis.get("teachings", []):
            start, end = find_timestamp(teaching["text"], segments)
            teaching["start"] = start
            teaching["end"] = end

        # Enrich viral moments
        for moment in analysis.get("viral_moments", []):
            start, end = find_timestamp(moment["text"], segments)
            moment["start"] = start
            moment["end"] = end

        return analysis

    async def generate_clips_from_analysis(self, analysis: Dict, min_duration: float = 15, max_duration: float = 120) -> List[Dict]:
        """
        Gera sugestões de clips baseados na análise.
        
        Args:
            analysis: Análise completa da transcrição
            min_duration: Duração mínima do clip em segundos (padrão: 15s)
            max_duration: Duração máxima do clip em segundos (padrão: 120s)
            
        Returns:
            Lista de clips sugeridos
        """
        clips = []
        
        # Combinar todos os momentos identificados
        all_moments = []
        
        for story in analysis.get("stories", []):
            if story.get("start") and story.get("end"):
                all_moments.append({
                    "type": "story",
                    "text": story["text"],
                    "start": story["start"],
                    "end": story["end"],
                    "score": story["score"],
                    "summary": story["summary"]
                })
        
        for joke in analysis.get("jokes", []):
            if joke.get("start") and joke.get("end"):
                all_moments.append({
                    "type": "joke",
                    "text": joke["text"],
                    "start": joke["start"],
                    "end": joke["end"],
                    "score": joke["score"]
                })
        
        for controversy in analysis.get("controversies", []):
            if controversy.get("start") and controversy.get("end"):
                all_moments.append({
                    "type": "controversy",
                    "text": controversy["text"],
                    "start": controversy["start"],
                    "end": controversy["end"],
                    "score": controversy["score"],
                    "topic": controversy["topic"]
                })
        
        for teaching in analysis.get("teachings", []):
            if teaching.get("start") and teaching.get("end"):
                all_moments.append({
                    "type": "teaching",
                    "text": teaching["text"],
                    "start": teaching["start"],
                    "end": teaching["end"],
                    "score": teaching["score"],
                    "lesson": teaching["lesson"]
                })
        
        for moment in analysis.get("viral_moments", []):
            if moment.get("start") and moment.get("end"):
                all_moments.append({
                    "type": moment["type"],
                    "text": moment["text"],
                    "start": moment["start"],
                    "end": moment["end"],
                    "score": moment["score"],
                    "reason": moment["reason"]
                })
        
        # Ordenar por score
        all_moments.sort(key=lambda x: x["score"], reverse=True)
        
        # Adicionar buffer de 5 segundos antes e depois (reduzido de 8s)
        for moment in all_moments:
            moment["start"] = max(0, moment["start"] - 5)
            moment["end"] = moment["end"] + 5
            moment["duration"] = moment["end"] - moment["start"]
        
        # Filtrar por duração (mais flexível: 15s a 120s)
        filtered_moments = [
            m for m in all_moments
            if min_duration <= m["duration"] <= max_duration
        ]
        
        # Se não houver clips suficientes, tentar sem filtro de duração máxima
        if len(filtered_moments) < 5:
            filtered_moments = [
                m for m in all_moments
                if m["duration"] >= min_duration
            ]
        
        return filtered_moments[:15]  # Retornar top 15 clips (aumentado de 10)
