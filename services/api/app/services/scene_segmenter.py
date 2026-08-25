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

        text = script_raw.strip()
        scenes_data: List[dict] = []

        # 1. Tentar divisão por cabeçalhos explícitos
        scene_header_pattern = re.compile(
            r"(?:^|\n+)[ \t]*(?:\[?(?:Cena|Scene|CENA|SCENE)\s*(\d+)[\:\-\]\s]+)"
            r"(.*?)(?=(?:\n+[ \t]*\[?(?:Cena|Scene|CENA|SCENE)\s*\d+[\:\-\]\s]+)|$)",
            re.DOTALL | re.IGNORECASE,
        )

        matches = list(scene_header_pattern.finditer(text))

        if matches and len(matches) > 1:
            for match in matches:
                header_num = match.group(1)
                content = match.group(2).strip()

                lines = [line.strip() for line in content.split("\n") if line.strip()]
                if not lines:
                    continue

                title = f"Cena {int(header_num):02d}"
                narration = content

                if len(lines) > 1 and len(lines[0]) < 60:
                    title = f"Cena {int(header_num):02d}: {lines[0]}"
                    narration = "\n".join(lines[1:]).strip()

                scenes_data.append(
                    {
                        "title": title,
                        "narration": narration,
                    }
                )
        else:
            # 2. Fallback: Divisão por blocos de parágrafos
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]

            if len(paragraphs) > 1:
                for idx, paragraph in enumerate(paragraphs, start=1):
                    scenes_data.append(
                        {
                            "title": f"Cena {idx:02d}",
                            "narration": paragraph,
                        }
                    )
            else:
                # 3. Fallback: Se for um bloco único longo, dividir a cada ~30 palavras
                sentences = re.split(r"(?<=[.!?])\s+", text)
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
