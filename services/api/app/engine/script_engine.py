import logging
import re
from typing import Optional

import httpx

from app.core.config import settings
from app.domain.enums import ScriptTone
from app.domain.schemas import GenerateScriptResponse

logger = logging.getLogger("framescout.engine.script")

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_GENERATE_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)


class ScriptEngine:
    """
    Motor de geração e roteirização inteligente com IA (Google Gemini Copilot).
    Transforma temas brutos, notícias ou ideias em roteiros estruturados cena a cena
    com ganchos de retenção, arcos narrativos e formatação otimizada para o FrameScout.
    """

    @classmethod
    async def generate_script(
        cls,
        topic: str,
        tone: ScriptTone = ScriptTone.DOCUMENTARY,
        target_duration: str = "3m",
        language: str = "pt-BR",
        context_notes: Optional[str] = None,
    ) -> GenerateScriptResponse:
        clean_topic = topic.strip()
        if not clean_topic:
            clean_topic = "Tecnologia e Inovação"

        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key.strip() in ["", "mock", "test"]:
            return cls._generate_contingency_script(clean_topic, tone, target_duration)

        try:
            return await cls._generate_remote_gemini(
                api_key=api_key,
                topic=clean_topic,
                tone=tone,
                target_duration=target_duration,
                language=language,
                context_notes=context_notes,
            )
        except Exception as exc:
            logger.warning(
                f"Falha na chamada ao Gemini para roteirização ({exc}). "
                "Recorrendo ao gerador de contingência."
            )
            return cls._generate_contingency_script(clean_topic, tone, target_duration)

    @classmethod
    async def _generate_remote_gemini(
        cls,
        api_key: str,
        topic: str,
        tone: ScriptTone,
        target_duration: str,
        language: str,
        context_notes: Optional[str],
    ) -> GenerateScriptResponse:
        word_target = 380
        sec_target = 180
        if target_duration in ["60s", "1m", "shorts"]:
            word_target = 140
            sec_target = 60
        elif target_duration in ["5m"]:
            word_target = 650
            sec_target = 300
        elif target_duration in ["10m"]:
            word_target = 1300
            sec_target = 600

        tone_instructions = {
            ScriptTone.DOCUMENTARY: (
                "Tom investigativo, sério, profundo e cinematográfico, estilo LOG FATAL e Vox. "
                "Foco em fatos, tensões e impactos reais."
            ),
            ScriptTone.TECH_NEWS: (
                "Tom dinâmico de notícias e bastidores da tecnologia. "
                "Rápido, informativo e com ganchos claros."
            ),
            ScriptTone.EXPLAINER: (
                "Tom didático, educativo e envolvente. Use metáforas simples "
                "para explicar conceitos complexos de forma cativante."
            ),
            ScriptTone.VIRAL_SHORTS: (
                "Tom elétrico de altíssima retenção para TikTok/Shorts. Gancho impactante "
                "nos primeiros 3 segundos, frases curtas e ritmo acelerado."
            ),
            ScriptTone.DRAMATIC_STORYTELLING: (
                "Tom dramático, com suspense, reviravoltas e foco no drama humano e corporativo."
            ),
        }.get(tone, "Tom documental e envolvente.")

        notes_prompt = (
            f"\nNotas e pontos-chave adicionais: {context_notes}" if context_notes else ""
        )

        system_instruction = (
            f"Você é um dos melhores roteiristas de documentários em vídeo do mundo.\n"
            f"Sua missão é criar um roteiro completo em {language} sobre: '{topic}'.\n"
            f"Diretriz de Tom: {tone_instructions}\n"
            f"Meta: ~{word_target} palavras (~{sec_target}s falados).\n"
            f"{notes_prompt}\n\n"
            f"REGRAS DE FORMATAÇÃO OBRIGATÓRIAS:\n"
            f"1. Divida o roteiro em Cenas numeradas sequencialmente.\n"
            f"2. Cada cena DEVE iniciar com: 'Cena XX: [Título da Cena]'\n"
            f"3. Abaixo do título, coloque a narração em parágrafos diretos e fluidos.\n"
            f"4. A Cena 01 DEVE conter um Gancho (Hook) magnético nos primeiros 5 segundos.\n"
            f"5. A última cena DEVE conter uma reflexão final ou Call-to-Action (CTA).\n"
            f"6. NÃO inclua instruções entre colchetes para leitura TTS perfeita.\n"
            f"7. Comece o texto na primeira linha com '# Titulo: [Título]'\n"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": system_instruction}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            },
        }

        url = f"{GEMINI_GENERATE_URL}?key={api_key}"
        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            if res.status_code != 200:
                logger.warning(
                    f"Gemini generateContent retornou status {res.status_code}: {res.text[:150]}"
                )
                return cls._generate_contingency_script(topic, tone, target_duration)

            data = res.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return cls._generate_contingency_script(topic, tone, target_duration)

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not raw_text or len(raw_text.strip()) < 50:
                return cls._generate_contingency_script(topic, tone, target_duration)

            return cls._parse_generated_script(raw_text, topic, tone, sec_target)

    @classmethod
    def _parse_generated_script(
        cls,
        text: str,
        topic: str,
        tone: ScriptTone,
        default_seconds: int,
    ) -> GenerateScriptResponse:
        lines = text.strip().splitlines()
        title = f"Documentário: {topic}"

        cleaned_lines = []
        for line in lines:
            if (
                line.startswith("# Titulo:")
                or line.startswith("# Título:")
                or line.startswith("# Title:")
            ):
                title = re.sub(r"^#\s*T[ií]tulo:\s*", "", line, flags=re.IGNORECASE).strip()
            else:
                cleaned_lines.append(line)

        script_raw = "\n".join(cleaned_lines).strip()
        word_count = len(script_raw.split())
        est_seconds = max(30, round((word_count / 130) * 60))

        # Extrair gancho (primeira cena) e CTA (última cena)
        scenes_blocks = re.split(r"(?:^|\n)(?=Cena\s+\d+:)", script_raw, flags=re.IGNORECASE)
        scenes_blocks = [b.strip() for b in scenes_blocks if b.strip()]

        hook = None
        cta = None
        if scenes_blocks:
            hook = scenes_blocks[0][:200]
            if len(scenes_blocks) > 1:
                cta = scenes_blocks[-1][:200]

        return GenerateScriptResponse(
            title=title,
            topic=topic,
            tone=tone,
            estimated_duration_seconds=est_seconds or default_seconds,
            word_count=word_count,
            script_raw=script_raw,
            hook=hook,
            call_to_action=cta,
        )

    @classmethod
    def _generate_contingency_script(
        cls,
        topic: str,
        tone: ScriptTone,
        target_duration: str,
    ) -> GenerateScriptResponse:
        """
        Gera um roteiro temático completo e estruturado para uso offline ou em contingência.
        """
        title = f"Os Bastidores Ocultos: {topic}"
        is_shorts = target_duration in ["60s", "1m", "shorts"]

        if is_shorts:
            script_raw = (
                f"Cena 01: O Início Inesperado\n"
                f"Você já parou para pensar em como {topic} mudou tudo o que conhecemos? "
                f"Em poucos segundos, o cenário mundial se transformou.\n\n"
                f"Cena 02: O Ponto de Ruptura\n"
                f"Especialistas e analistas não esperavam uma reviravolta tão rápida. "
                f"Sistemas inteiros entraram em alerta e o impacto foi imediato.\n\n"
                f"Cena 03: O Desfecho e o Futuro\n"
                f"O que parecia um detalhe isolado revelou uma falha crítica. "
                f"Qual é a sua opinião sobre isso? Deixe nos comentários e siga o canal."
            )
        else:
            script_raw = (
                f"Cena 01: O Ponto de Partida\n"
                f"Quando pensamos em grandes transformações na tecnologia e na sociedade, "
                f"poucos eventos chamam tanta atenção quanto {topic}.\n\n"
                f"Cena 02: O Cenário Crítico\n"
                f"Nos bastidores, engenheiros e autoridades tentavam conter as repercussões. "
                f"A cada minuto, novos dados mostravam a gravidade da situação.\n\n"
                f"Cena 03: A Revelação e os Fatos Ocultos\n"
                f"Investigações detalhadas trouxeram à tona fatores decisivos. "
                f"Não se tratava de um evento pontual, mas de um sintoma de um sistema frágil.\n\n"
                f"Cena 04: Conclusão e Lições Aprendidas\n"
                f"Hoje, o caso de {topic} serve como um marco definitivo para o futuro. "
                f"Inscreva-se no canal e acompanhe nossas próximas análises."
            )

        word_count = len(script_raw.split())
        est_seconds = max(30, round((word_count / 130) * 60))

        return GenerateScriptResponse(
            title=title,
            topic=topic,
            tone=tone,
            estimated_duration_seconds=est_seconds,
            word_count=word_count,
            script_raw=script_raw,
            hook=f"Quando pensamos em grandes transformações... {topic}",
            call_to_action="Inscreva-se no canal para acompanhar mais análises.",
        )
