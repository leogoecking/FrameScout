from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas import (
    SceneCreate,
    SceneMergeRequest,
    SceneSplitRequest,
    SceneUpdate,
)
from app.models.entities import Project, Scene
from app.services.scene_segmenter import (
    ScriptSegmenter,
    estimate_duration_seconds,
    infer_visual_intent,
)


class SceneService:
    @staticmethod
    async def list_by_project(db: AsyncSession, project_id: UUID) -> List[Scene]:
        query = (
            select(Scene)
            .where(Scene.project_id == project_id)
            .order_by(Scene.position.asc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get(db: AsyncSession, scene_id: UUID) -> Optional[Scene]:
        query = select(Scene).where(Scene.id == scene_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def generate_from_script(
        db: AsyncSession, project_id: UUID, overwrite: bool = True
    ) -> List[Scene]:
        # Fetch project
        proj_query = select(Project).where(Project.id == project_id)
        proj_res = await db.execute(proj_query)
        project = proj_res.scalar_one_or_none()

        if not project:
            raise ValueError("Projeto não encontrado")

        if not project.script_raw or not project.script_raw.strip():
            raise ValueError("O projeto não possui um roteiro salvo para segmentar.")

        # Segment raw script
        scenes_data = ScriptSegmenter.segment(project.script_raw)

        if overwrite:
            # Delete existing scenes
            del_stmt = delete(Scene).where(Scene.project_id == project_id)
            await db.execute(del_stmt)

        created_scenes: List[Scene] = []
        for s in scenes_data:
            scene = Scene(
                project_id=project_id,
                position=s.position or 1,
                title=s.title,
                narration=s.narration,
                visual_intent=s.visual_intent,
                start_estimate=s.start_estimate,
                end_estimate=s.end_estimate,
            )
            db.add(scene)
            created_scenes.append(scene)

        await db.commit()
        for sc in created_scenes:
            await db.refresh(sc)

        return created_scenes

    @staticmethod
    async def create(
        db: AsyncSession, project_id: UUID, obj_in: SceneCreate
    ) -> Scene:
        # Determine next position if not given
        if obj_in.position is None:
            existing = await SceneService.list_by_project(db, project_id)
            pos = len(existing) + 1
        else:
            pos = obj_in.position

        dur = estimate_duration_seconds(obj_in.narration)
        start_est = obj_in.start_estimate or 0.0
        end_est = obj_in.end_estimate or round(start_est + dur, 1)
        intent = obj_in.visual_intent or infer_visual_intent(obj_in.narration)

        scene = Scene(
            project_id=project_id,
            position=pos,
            title=obj_in.title or f"Cena {pos:02d}",
            narration=obj_in.narration,
            visual_intent=intent,
            start_estimate=start_est,
            end_estimate=end_est,
        )
        db.add(scene)
        await db.commit()
        await db.refresh(scene)
        return scene

    @staticmethod
    async def update(
        db: AsyncSession, scene: Scene, obj_in: SceneUpdate
    ) -> Scene:
        if obj_in.title is not None:
            scene.title = obj_in.title
        if obj_in.narration is not None:
            scene.narration = obj_in.narration
            # Recalculate duration if time wasn't explicitly supplied
            if obj_in.end_estimate is None and scene.start_estimate is not None:
                dur = estimate_duration_seconds(obj_in.narration)
                scene.end_estimate = round(scene.start_estimate + dur, 1)
        if obj_in.visual_intent is not None:
            scene.visual_intent = obj_in.visual_intent
        if obj_in.start_estimate is not None:
            scene.start_estimate = obj_in.start_estimate
        if obj_in.end_estimate is not None:
            scene.end_estimate = obj_in.end_estimate
        if obj_in.position is not None:
            scene.position = obj_in.position

        await db.commit()
        await db.refresh(scene)
        return scene

    @staticmethod
    async def delete(db: AsyncSession, scene: Scene) -> None:
        project_id = scene.project_id
        await db.delete(scene)
        await db.commit()

        # Re-index remaining positions
        remaining = await SceneService.list_by_project(db, project_id)
        for idx, sc in enumerate(remaining, start=1):
            sc.position = idx
        await db.commit()

    @staticmethod
    async def reorder(
        db: AsyncSession, project_id: UUID, scene_ids: List[UUID]
    ) -> List[Scene]:
        scenes = await SceneService.list_by_project(db, project_id)
        scene_map = {sc.id: sc for sc in scenes}

        current_time = 0.0
        reordered: List[Scene] = []

        for idx, sc_id in enumerate(scene_ids, start=1):
            if sc_id in scene_map:
                sc = scene_map[sc_id]
                sc.position = idx
                dur = (
                    sc.end_estimate - sc.start_estimate
                    if sc.end_estimate and sc.start_estimate
                    else estimate_duration_seconds(sc.narration)
                )
                sc.start_estimate = round(current_time, 1)
                sc.end_estimate = round(current_time + dur, 1)
                current_time = sc.end_estimate
                reordered.append(sc)

        await db.commit()
        return reordered

    @staticmethod
    async def split(
        db: AsyncSession, scene: Scene, split_data: SceneSplitRequest
    ) -> List[Scene]:
        project_id = scene.project_id
        orig_pos = scene.position
        orig_start = scene.start_estimate or 0.0

        # Part 1: Update existing scene
        dur1 = estimate_duration_seconds(split_data.first_part_narration)
        scene.narration = split_data.first_part_narration
        if split_data.first_part_title:
            scene.title = split_data.first_part_title
        if split_data.first_part_visual_intent:
            scene.visual_intent = split_data.first_part_visual_intent
        scene.start_estimate = orig_start
        scene.end_estimate = round(orig_start + dur1, 1)

        # Shift all subsequent scenes by +1 position
        remaining = await SceneService.list_by_project(db, project_id)
        for sc in remaining:
            if sc.position > orig_pos:
                sc.position += 1

        # Part 2: Create new second scene
        dur2 = estimate_duration_seconds(split_data.second_part_narration)
        start2 = scene.end_estimate
        end2 = round(start2 + dur2, 1)
        intent2 = (
            split_data.second_part_visual_intent
            or infer_visual_intent(split_data.second_part_narration)
        )

        new_scene = Scene(
            project_id=project_id,
            position=orig_pos + 1,
            title=split_data.second_part_title or f"Cena {orig_pos + 1:02d}",
            narration=split_data.second_part_narration,
            visual_intent=intent2,
            start_estimate=start2,
            end_estimate=end2,
        )
        db.add(new_scene)
        await db.commit()
        await db.refresh(scene)
        await db.refresh(new_scene)

        return [scene, new_scene]

    @staticmethod
    async def merge(
        db: AsyncSession, scene1: Scene, req: SceneMergeRequest
    ) -> Scene:
        scene2 = await SceneService.get(db, req.target_scene_id)
        if not scene2 or scene2.project_id != scene1.project_id:
            raise ValueError("Segunda cena não encontrada no mesmo projeto")

        # Merge narration and times
        scene1.narration = f"{scene1.narration.strip()}\n\n{scene2.narration.strip()}"
        if scene2.end_estimate and scene1.start_estimate is not None:
            scene1.end_estimate = scene2.end_estimate
        else:
            dur = estimate_duration_seconds(scene1.narration)
            scene1.end_estimate = round((scene1.start_estimate or 0.0) + dur, 1)

        # Delete scene2
        await db.delete(scene2)
        await db.commit()

        # Re-index positions
        remaining = await SceneService.list_by_project(db, scene1.project_id)
        for idx, sc in enumerate(remaining, start=1):
            sc.position = idx

        await db.commit()
        await db.refresh(scene1)
        return scene1
