"use client";

import { useState, useEffect } from "react";
import { Scene, SceneSplitRequest, SceneUpdate, SearchQuery } from "@/types";
import { 
  createScene, 
  deleteScene, 
  generateProjectQueries, 
  generateScenes, 
  listScenes,
  mergeScenes, 
  reorderScenes, 
  splitScene, 
  updateScene 
} from "@/lib/api-client";
import { SceneCard } from "@/components/SceneCard";
import { SplitSceneModal } from "@/components/SplitSceneModal";
import { 
  Sparkles, 
  Plus, 
  Clock, 
  Layers, 
  Loader2, 
  AlertCircle,
  Search,
  CheckCircle2
} from "lucide-react";

interface SceneListProps {
  projectId: string;
  hasScript: boolean;
  initialScenes: Scene[];
  onScenesUpdated?: (scenes: Scene[]) => void;
  onAssetSelected?: () => void;
}

export function SceneList({
  projectId,
  hasScript,
  initialScenes,
  onScenesUpdated,
  onAssetSelected,
}: SceneListProps) {
  const [scenes, setScenes] = useState<Scene[]>(initialScenes);
  const [isGeneratingScenes, setIsGeneratingScenes] = useState(false);
  const [isGeneratingQueries, setIsGeneratingQueries] = useState(false);
  const [isCreatingManual, setIsCreatingManual] = useState(false);
  const [splitTargetScene, setSplitTargetScene] = useState<Scene | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    setScenes(initialScenes);
  }, [initialScenes]);

  const notifyUpdated = (newScenes: Scene[]) => {
    setScenes(newScenes);
    if (onScenesUpdated) {
      onScenesUpdated(newScenes);
    }
  };

  const handleGenerateScenes = async () => {
    if (!hasScript) {
      setError("Por favor, adicione e salve um roteiro antes de gerar cenas.");
      return;
    }

    setIsGeneratingScenes(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const generated = await generateScenes(projectId);
      notifyUpdated(generated);
      setSuccessMessage(`Roteiro segmentado em ${generated.length} cenas com sucesso!`);
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      setError(err?.message || "Erro ao gerar cenas.");
    } finally {
      setIsGeneratingScenes(false);
    }
  };

  const handleBatchGenerateQueries = async () => {
    if (scenes.length === 0) {
      setError("Crie ou gere cenas antes de produzir consultas de busca.");
      return;
    }

    setIsGeneratingQueries(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const res = await generateProjectQueries(projectId);
      // Reload scenes with their queries populated
      const refreshed = await listScenes(projectId);
      notifyUpdated(refreshed);
      setSuccessMessage(
        `${res.total_queries_created} consultas de busca geradas para ${res.scenes_count} cenas!`
      );
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (err: any) {
      setError(err?.message || "Erro ao gerar queries em lote.");
    } finally {
      setIsGeneratingQueries(false);
    }
  };

  const handleCreateManual = async () => {
    setIsCreatingManual(true);
    setError(null);
    try {
      const nextPos = scenes.length + 1;
      const created = await createScene(projectId, {
        title: `Cena ${nextPos.toString().padStart(2, "0")}`,
        narration: "Digite a narração para esta nova cena...",
        visual_intent: "Defina a intenção visual para a busca de mídia...",
      });
      notifyUpdated([...scenes, created]);
    } catch (err: any) {
      setError(err?.message || "Erro ao criar nova cena.");
    } finally {
      setIsCreatingManual(false);
    }
  };

  const handleUpdate = async (sceneId: string, data: SceneUpdate) => {
    try {
      const updated = await updateScene(sceneId, data);
      notifyUpdated(scenes.map((s) => (s.id === sceneId ? updated : s)));
    } catch (err: any) {
      setError(err?.message || "Erro ao atualizar cena.");
    }
  };

  const handleDelete = async (sceneId: string) => {
    try {
      await deleteScene(sceneId);
      const remaining = scenes
        .filter((s) => s.id !== sceneId)
        .map((s, idx) => ({ ...s, position: idx + 1 }));
      notifyUpdated(remaining);
    } catch (err: any) {
      setError(err?.message || "Erro ao excluir cena.");
    }
  };

  const handleMove = async (sceneId: string, direction: "up" | "down") => {
    const idx = scenes.findIndex((s) => s.id === sceneId);
    if (idx === -1) return;
    if (direction === "up" && idx === 0) return;
    if (direction === "down" && idx === scenes.length - 1) return;

    const newScenes = [...scenes];
    const targetIdx = direction === "up" ? idx - 1 : idx + 1;
    const temp = newScenes[idx];
    newScenes[idx] = newScenes[targetIdx];
    newScenes[targetIdx] = temp;

    const sceneIds = newScenes.map((s) => s.id);
    try {
      const reordered = await reorderScenes(projectId, sceneIds);
      notifyUpdated(reordered);
    } catch (err: any) {
      setError(err?.message || "Erro ao reordenar cenas.");
    }
  };

  const handleSplit = async (sceneId: string, data: SceneSplitRequest) => {
    try {
      const splitResult = await splitScene(sceneId, data);
      const idx = scenes.findIndex((s) => s.id === sceneId);
      if (idx !== -1) {
        const nextScenes = [
          ...scenes.slice(0, idx),
          ...splitResult,
          ...scenes.slice(idx + 1).map((s) => ({ ...s, position: s.position + 1 })),
        ];
        notifyUpdated(nextScenes);
      }
    } catch (err: any) {
      setError(err?.message || "Erro ao dividir cena.");
    }
  };

  const handleMergeWithNext = async (scene: Scene) => {
    const idx = scenes.findIndex((s) => s.id === scene.id);
    if (idx === -1 || idx === scenes.length - 1) return;

    const nextScene = scenes[idx + 1];
    if (
      confirm(
        `Unir Cena ${scene.position} com Cena ${nextScene.position}? O texto de ambas será mesclado.`
      )
    ) {
      try {
        const merged = await mergeScenes(scene.id, nextScene.id);
        const nextScenes = scenes
          .filter((s) => s.id !== nextScene.id)
          .map((s) => (s.id === scene.id ? merged : s))
          .map((s, i) => ({ ...s, position: i + 1 }));
        notifyUpdated(nextScenes);
      } catch (err: any) {
        setError(err?.message || "Erro ao unir cenas.");
      }
    }
  };

  const handleQueriesUpdated = (sceneId: string, queries: SearchQuery[]) => {
    const updated = scenes.map((s) => (s.id === sceneId ? { ...s, queries } : s));
    notifyUpdated(updated);
  };

  // Total Duration and Total Queries count
  const totalSeconds = scenes.reduce((acc, s) => {
    const dur = (s.end_estimate || 0) - (s.start_estimate || 0);
    return acc + Math.max(0, dur);
  }, 0);
  const totalMins = Math.floor(totalSeconds / 60);
  const remSecs = Math.floor(totalSeconds % 60);

  const totalQueries = scenes.reduce((acc, s) => acc + (s.queries?.length || 0), 0);

  return (
    <div className="space-y-6">
      {/* Control Bar */}
      <div className="glass-panel p-4 rounded-2xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-mono font-semibold">
            <Layers className="h-3.5 w-3.5" />
            <span>{scenes.length} {scenes.length === 1 ? "Cena" : "Cenas"}</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-semibold">
            <Search className="h-3.5 w-3.5" />
            <span>{totalQueries} {totalQueries === 1 ? "Busca" : "Buscas"}</span>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
            <Clock className="h-3.5 w-3.5 text-slate-500" />
            <span>Duração: {totalMins}m {remSecs}s</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleCreateManual}
            disabled={isCreatingManual}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-white/10 transition-all"
          >
            {isCreatingManual ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plus className="h-3.5 w-3.5" />}
            <span>Nova Cena</span>
          </button>

          {scenes.length > 0 && (
            <button
              onClick={handleBatchGenerateQueries}
              disabled={isGeneratingQueries}
              className="px-3.5 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold flex items-center gap-1.5 transition-all disabled:opacity-50"
            >
              {isGeneratingQueries ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Gerando Queries...</span>
                </>
              ) : (
                <>
                  <Search className="h-3.5 w-3.5" />
                  <span>Gerar Queries em Lote</span>
                </>
              )}
            </button>
          )}

          <button
            onClick={handleGenerateScenes}
            disabled={isGeneratingScenes || !hasScript}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-blue-600/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isGeneratingScenes ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Segmentando Roteiro...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-3.5 w-3.5" />
                <span>{scenes.length > 0 ? "Regerar Cenas" : "Gerar Cenas do Roteiro"}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Scenes Timeline / Cards */}
      {scenes.length === 0 ? (
        <div className="glass-panel p-12 rounded-3xl text-center space-y-4 border-dashed border-white/10">
          <div className="inline-flex p-4 rounded-2xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Layers className="h-8 w-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-semibold text-white">Nenhuma cena criada ainda</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              Use o botão acima para segmentar automaticamente seu roteiro em cenas ou crie cenas manualmente.
            </p>
          </div>
          <div className="flex items-center justify-center gap-3 pt-2">
            <button
              onClick={handleGenerateScenes}
              disabled={!hasScript}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 disabled:opacity-50 transition-all"
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Gerar Cenas Automaticamente</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {scenes.map((scene, idx) => (
            <SceneCard
              key={scene.id}
              scene={scene}
              isFirst={idx === 0}
              isLast={idx === scenes.length - 1}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
              onMoveUp={(id) => handleMove(id, "up")}
              onMoveDown={(id) => handleMove(id, "down")}
              onOpenSplit={(sc) => setSplitTargetScene(sc)}
              onMergeWithNext={handleMergeWithNext}
              onQueriesUpdated={handleQueriesUpdated}
              onAssetSelected={onAssetSelected}
            />
          ))}
        </div>
      )}

      {/* Split Modal */}
      <SplitSceneModal
        scene={splitTargetScene}
        isOpen={!!splitTargetScene}
        onClose={() => setSplitTargetScene(null)}
        onSplit={handleSplit}
      />
    </div>
  );
}
