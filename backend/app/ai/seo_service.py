from typing import Dict, List, Optional
import google.generativeai as genai
from app.core.config import settings


class SEOService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    async def generate_titles(self, clip_text: str, category: str, count: int = 10) -> List[str]:
        """
        Gera títulos otimizados para SEO.

        Args:
            clip_text: Texto do clip
            category: Categoria do clip
            count: Número de títulos a gerar

        Returns:
            Lista de títulos gerados
        """
        if not self.model:
            raise Exception("Gemini API key not configured")

        prompt = f"""
Gere {count} títulos otimizados para SEO para um vídeo curto (Short/Reel/TikTok).

Contexto:
- Texto do vídeo: {clip_text}
- Categoria: {category}

Os títulos devem:
1. Ser chamativos e clicáveis
2. Ter entre 20-60 caracteres
3. Usar gatilhos emocionais ou curiosidade
4. Ser relevantes para o conteúdo
5. Funcionar bem em redes sociais

Retorne apenas os títulos, um por linha.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=500
                )
            )

            titles = response.text.strip().split('\n')
            return [title.strip() for title in titles if title.strip()]

        except Exception as e:
            raise Exception(f"Gemini title generation error: {str(e)}")

    async def generate_description(self, clip_text: str, category: str, max_length: int = 500) -> str:
        """
        Gera descrição otimizada para SEO.

        Args:
            clip_text: Texto do clip
            category: Categoria do clip
            max_length: Comprimento máximo da descrição

        Returns:
            Descrição gerada
        """
        if not self.model:
            raise Exception("Gemini API key not configured")

        prompt = f"""
Gere uma descrição otimizada para SEO para um vídeo curto (Short/Reel/TikTok).

Contexto:
- Texto do vídeo: {clip_text}
- Categoria: {category}

A descrição deve:
1. Ser envolvente desde o início
2. Incluir palavras-chave relevantes
3. Ter no máximo {max_length} caracteres
4. Incluir uma call-to-action sutil
5. Ser adequada para redes sociais

Retorne apenas a descrição.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=400
                )
            )

            description = response.text.strip()
            return description[:max_length]

        except Exception as e:
            raise Exception(f"Gemini description generation error: {str(e)}")

    async def generate_hashtags(self, clip_text: str, category: str, count: int = 15) -> List[str]:
        """
        Gera hashtags relevantes para o conteúdo.

        Args:
            clip_text: Texto do clip
            category: Categoria do clip
            count: Número de hashtags a gerar

        Returns:
            Lista de hashtags geradas
        """
        if not self.model:
            raise Exception("Gemini API key not configured")

        prompt = f"""
Gere {count} hashtags relevantes para um vídeo curto (Short/Reel/TikTok).

Contexto:
- Texto do vídeo: {clip_text}
- Categoria: {category}

As hashtags devem:
1. Ser relevantes para o conteúdo
2. Incluir hashtags populares da categoria
3. Incluir hashtags específicas do nicho
4. Misturar hashtags populares e específicas
5. Estar no formato #hashtag

Retorne apenas as hashtags, separadas por espaço.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=300
                )
            )

            hashtags_text = response.text.strip()
            hashtags = [tag.strip() for tag in hashtags_text.split() if tag.startswith('#')]
            return hashtags[:count]

        except Exception as e:
            raise Exception(f"Gemini hashtag generation error: {str(e)}")

    async def generate_complete_seo(
        self,
        clip_text: str,
        category: str,
        titles_count: int = 10,
        hashtags_count: int = 15
    ) -> Dict:
        """
        Gera conteúdo SEO completo (títulos, descrição, hashtags).
        
        Args:
            clip_text: Texto do clip
            category: Categoria do clip
            titles_count: Número de títulos a gerar
            hashtags_count: Número de hashtags a gerar
            
        Returns:
            Dicionário com títulos, descrição e hashtags
        """
        titles = await self.generate_titles(clip_text, category, titles_count)
        description = await self.generate_description(clip_text, category)
        hashtags = await self.generate_hashtags(clip_text, category, hashtags_count)

        return {
            "titles": titles,
            "description": description,
            "hashtags": hashtags
        }

    async def extract_keywords(self, text: str, count: int = 10) -> List[str]:
        """
        Extrai palavras-chave do texto.

        Args:
            text: Texto para análise
            count: Número de palavras-chave a extrair

        Returns:
            Lista de palavras-chave
        """
        if not self.model:
            raise Exception("Gemini API key not configured")

        prompt = f"""
Extraia as {count} palavras-chave mais importantes do seguinte texto:

Texto: {text}

Retorne apenas as palavras-chave, uma por linha.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=200
                )
            )

            keywords = response.text.strip().split('\n')
            return [keyword.strip() for keyword in keywords if keyword.strip()]

        except Exception as e:
            raise Exception(f"Gemini keyword extraction error: {str(e)}")
