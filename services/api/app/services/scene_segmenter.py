import re
from typing import List

from app.domain.schemas import SceneCreate

# Words per minute for speech rate estimation (~2.16 words/sec)
WORDS_PER_MINUTE = 130.0


def estimate_duration_seconds(text: str) -> float:
    words = len(text.strip().split()) if text.strip() else 0
    # Minimum 3.0 seconds per scene
    return max(3.0, round((words / WORDS_PER_MINUTE) * 60.0, 1))


def infer_visual_intent(narration: str) -> str:
    """
    Dedução heurística inicial de intenção visual com base no conteúdo narrativo.
    """
    lower = narration.lower()

    if any(k in lower for k in ["tela azul", "bsod", "crash", "erro", "pane"]):
        return "B-roll de tela azul da morte (BSOD) ou monitores com falhas de sistema"
    elif any(k in lower for k in ["aeroporto", "voo", "avião", "embarque"]):
        return "B-roll de painel de voos cancelados ou saguão de aeroporto lotado"
    elif any(k in lower for k in ["hospital", "médico", "saúde", "atendimento"]):
        return "B-roll de computadores em ambiente hospitalar ou equipe médica"
    elif any(k in lower for k in ["servidor", "datacenter", "computador", "código", "software"]):
        return "B-roll de servidores em datacenter com luzes piscando ou terminal de código"
    elif any(k in lower for k in ["notícia", "jornal", "imprensa", "manchete"]):
        return "Imagens de manchetes de imprensa e cobertura jornalística do evento"
    elif any(k in lower for k in ["dinheiro", "banco", "caixa eletrônico", "pagamento"]):
        return "B-roll de caixa eletrônico com erro ou terminal financeiro"
    elif any(k in lower for k in ["crowdstrike", "microsoft", "windows"]):
        return "Logotipo corporativo e referências oficiais da empresa mencionada"
    else:
        words = narration.strip().split()
        first_few = " ".join(words[:6])
        return f"Material visual representativo: {first_few}..."


class ScriptSegmenter:
    """
    Motor heurístico de segmentação de roteiro em cenas.
    Opera 100% offline sem dependência de APIs externas.
    """

    @classmethod
    def segment(cls, script_raw: str) -> List[SceneCreate]:
        if not script_raw or not script_raw.strip():
            return []

        # 1. Limpar títulos globais do topo (ex: # Título: ...)
        clean_text = script_raw.strip()
        clean_text = re.sub(
            r"^(?:#+|\*\*|__)?\s*(?:T[ií]tulo|Title)\s*:\s*[^\n]+\n*",
            "",
            clean_text,
            flags=re.IGNORECASE,
        ).strip()

        scenes_data: List[dict] = []

        # 2. Tentar divisão por cabeçalhos explícitos (com suporte a markdown, bold, hashes, traços)
        header_pattern = re.compile(
            r"(?:^|\n+)[ \t]*(?:[#\*\-_>]*\s*\[?(?:Cena|Scene|CENA|SCENE)\s*"
            r"(\d+)[\:\-\]\s\*\_]*)([^\n]*)",
            re.IGNORECASE,
        )

        matches = list(header_pattern.finditer(clean_text))

        if matches and len(matches) >= 1:
            for i, match in enumerate(matches):
                scene_num = int(match.group(1))
                inline_title = match.group(2).strip().strip("*_#[]:- ")
                start_idx = match.end()
                end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(clean_text)
                content = clean_text[start_idx:end_idx].strip()

                title = f"Cena {scene_num:02d}"
                if inline_title:
                    title = f"Cena {scene_num:02d}: {inline_title}"
                elif content:
                    lines = [
                        ln.strip().strip("*_#[]:- ") for ln in content.split("\n") if ln.strip()
                    ]
                    if lines and len(lines[0]) < 60 and len(lines) > 1:
                        title = f"Cena {scene_num:02d}: {lines[0]}"
                        content = "\n".join(lines[1:]).strip()

                # Limpar markdown excessivo da narração
                narration = re.sub(r"^\s*[\*\-_]{2,}\s*", "", content).strip()
                narration = re.sub(r"\s*[\*\-_]{2,}\s*$", "", narration).strip()

                if narration or title:
                    scenes_data.append(
                        {
                            "title": title,
                            "narration": narration or title,
                        }
                    )
        else:
            # 3. Fallback: Divisão por blocos de parágrafos
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", clean_text) if p.strip()]

            if len(paragraphs) > 1:
                for idx, paragraph in enumerate(paragraphs, start=1):
                    scenes_data.append(
                        {
                            "title": f"Cena {idx:02d}",
                            "narration": paragraph,
                        }
                    )
            else:
                # 4. Fallback: Se for um bloco único longo, dividir a cada ~30 palavras
                sentences = re.split(r"(?<=[.!?])\s+", clean_text)
                current_chunk: List[str] = []
                scene_counter = 1

                for sentence in sentences:
                    current_chunk.append(sentence)
                    word_count = sum(len(s.split()) for s in current_chunk)
                    if word_count >= 30:
                        scenes_data.append(
                            {
                                "title": f"Cena {scene_counter:02d}",
                                "narration": " ".join(current_chunk),
                            }
                        )
                        current_chunk = []
                        scene_counter += 1

                if current_chunk:
                    scenes_data.append(
                        {
                            "title": f"Cena {scene_counter:02d}",
                            "narration": " ".join(current_chunk),
                        }
                    )

        # Construir objetos SceneCreate com timeline contínua
        results: List[SceneCreate] = []
        current_time = 0.0

        for idx, item in enumerate(scenes_data, start=1):
            narration = item["narration"]
            duration = estimate_duration_seconds(narration)
            start_est = round(current_time, 1)
            end_est = round(current_time + duration, 1)
            current_time = end_est

            visual_intent = infer_visual_intent(narration)

            results.append(
                SceneCreate(
                    position=idx,
                    title=item["title"],
                    narration=narration,
                    visual_intent=visual_intent,
                    start_estimate=start_est,
                    end_estimate=end_est,
                )
            )

        return results
