from typing import List, Set
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.schemas import (
    MediaCandidateRead,
    SceneVisualPlanItem,
    SelectedAssetRead,
    VisualPlanExport,
)
from app.models.entities import Project, Scene, SelectedAsset


class VisualPlanService:
    @staticmethod
    async def generate_visual_plan(db: AsyncSession, project_id: UUID) -> VisualPlanExport:
        # Carregar projeto com cenas e assets selecionados completos
        query = (
            select(Project)
            .options(
                selectinload(Project.scenes)
                .selectinload(Scene.selected_assets)
                .selectinload(SelectedAsset.media_candidate)
            )
            .where(Project.id == project_id)
        )
        res = await db.execute(query)
        project = res.scalar_one_or_none()
        if not project:
            raise KeyError("Projeto não encontrado")

        plan_items: List[SceneVisualPlanItem] = []
        consolidated_attributions: Set[str] = set()
        covered_count = 0
        total_duration = 0.0

        for scene in project.scenes:
            start = scene.start_estimate or 0.0
            end = scene.end_estimate or 0.0
            dur = max(0.0, end - start)
            total_duration += dur

            selected_asset_read: SelectedAssetRead | None = None
            if scene.selected_assets:
                sa = scene.selected_assets[0]
                mc_read: MediaCandidateRead | None = None
                if sa.media_candidate:
                    mc_read = MediaCandidateRead.model_validate(sa.media_candidate)
                    if sa.media_candidate.attribution:
                        consolidated_attributions.add(sa.media_candidate.attribution)
                    elif sa.media_candidate.author:
                        prov = sa.media_candidate.provider
                        consolidated_attributions.add(
                            f"Mídia por {sa.media_candidate.author} via {prov}"
                        )

                selected_asset_read = SelectedAssetRead(
                    id=sa.id,
                    scene_id=sa.scene_id,
                    media_candidate_id=sa.media_candidate_id,
                    order_index=sa.order_index,
                    framing_mode=sa.framing_mode,
                    notes=sa.notes,
                    created_at=sa.created_at,
                    media_candidate=mc_read,
                )
                covered_count += 1

            plan_items.append(
                SceneVisualPlanItem(
                    scene_position=scene.position,
                    scene_title=scene.title or f"Cena {scene.position}",
                    narration=scene.narration,
                    visual_intent=scene.visual_intent,
                    start_estimate=round(start, 2),
                    end_estimate=round(end, 2),
                    duration=round(dur, 2),
                    selected_asset=selected_asset_read,
                )
            )

        # Montar documento Markdown estruturado
        attributions_list = sorted(list(consolidated_attributions))
        md_doc = VisualPlanService._build_markdown_document(
            project_name=project.name,
            total_scenes=len(project.scenes),
            covered_count=covered_count,
            total_duration=total_duration,
            plan_items=plan_items,
            attributions=attributions_list,
        )

        return VisualPlanExport(
            project_id=project.id,
            project_name=project.name,
            language=project.language,
            total_scenes=len(project.scenes),
            covered_scenes_count=covered_count,
            total_duration_seconds=round(total_duration, 2),
            scenes=plan_items,
            consolidated_attributions=attributions_list,
            markdown_document=md_doc,
        )

    @staticmethod
    def _build_markdown_document(
        project_name: str,
        total_scenes: int,
        covered_count: int,
        total_duration: float,
        plan_items: List[SceneVisualPlanItem],
        attributions: List[str],
    ) -> str:
        mins = int(total_duration // 60)
        secs = int(total_duration % 60)
        coverage_pct = int((covered_count / total_scenes * 100)) if total_scenes > 0 else 0

        lines = [
            f"# Plano de Produção Visual — {project_name}",
            "",
            "## 📊 Resumo Executivo do Vídeo",
            f"- **Duração Estimada Total**: {mins:02d}:{secs:02d} ({total_duration:.1f}s)",
            f"- **Total de Cenas**: {total_scenes}",
            f"- **Cobertura de Mídia**: {covered_count}/{total_scenes} cenas ({coverage_pct}%)",
            "",
            "---",
            "",
            "## 🎬 Roteiro & Linha do Tempo Visual",
            "",
        ]

        for item in plan_items:
            m_start = int(item.start_estimate // 60)
            s_start = int(item.start_estimate % 60)
            m_end = int(item.end_estimate // 60)
            s_end = int(item.end_estimate % 60)
            tc = f"{m_start:02d}:{s_start:02d} ➔ {m_end:02d}:{s_end:02d} ({item.duration:.1f}s)"

            lines.append(f"### Cena {item.scene_position:02d}: {item.scene_title}")
            lines.append(f"**Tempo**: `{tc}`")
            lines.append(f'> *Narração*: "{item.narration}"')
            if item.visual_intent:
                lines.append(f"> *Direção de Arte*: {item.visual_intent}")
            lines.append("")

            if item.selected_asset and item.selected_asset.media_candidate:
                mc = item.selected_asset.media_candidate
                lines.append("#### 🖼️ Mídia Selecionada")
                lines.append(f"- **Título**: {mc.title or mc.external_id}")
                lines.append(f"- **Provedor**: `{mc.provider.upper()}`")
                lines.append(
                    f"- **Tipo / Resolução**: `{mc.media_type.value}` ({mc.width}x{mc.height})"
                )
                lines.append(f"- **Enquadramento**: `{item.selected_asset.framing_mode}`")
                lines.append(f"- **Status Jurídico**: `{mc.rights_status.value}`")
                lines.append(f"- **Link Original**: [{mc.url}]({mc.url})")
                if mc.preview_url:
                    lines.append(f"- **Arquivo/Prévia**: [{mc.preview_url}]({mc.preview_url})")
                if item.selected_asset.notes:
                    lines.append(f"- **Notas de Edição**: {item.selected_asset.notes}")
            else:
                lines.append("⚠️ *Nenhuma mídia selecionada para esta cena.*")

            lines.append("")
            lines.append("---")
            lines.append("")

        lines.append("## ⚖️ Créditos e Atribuições Consolidadas")
        lines.append(
            "*(Copie o bloco abaixo para incluir na descrição do vídeo ou créditos finais)*"
        )
        lines.append("")
        lines.append("```text")
        if attributions:
            for attr in attributions:
                lines.append(f"• {attr}")
        else:
            lines.append("Todas as mídias selecionadas são de Domínio Público ou licença livre.")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)
