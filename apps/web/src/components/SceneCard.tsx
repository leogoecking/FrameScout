"use client";

import { useState } from "react";
import { Scene, SceneUpdate, SearchQuery } from "@/types";
import { SceneQueriesSection } from "@/components/SceneQueriesSection";
import { 
  Clock, 
  ChevronUp, 
  ChevronDown, 
  Scissors, 
  Combine, 
  Trash2, 
  Eye, 
  Check, 
  Loader2 
} from "lucide-react";

interface SceneCardProps {
  scene: Scene;
  isFirst: boolean;
  isLast: boolean;
  onUpdate: (sceneId: string, data: SceneUpdate) => Promise<void>;
  onDelete: (sceneId: string) => Promise<void>;
  onMoveUp: (sceneId: string) => Promise<void>;
  onMoveDown: (sceneId: string) => Promise<void>;
  onOpenSplit: (scene: Scene) => void;
  onMergeWithNext: (scene: Scene) => Promise<void>;
  onQueriesUpdated?: (sceneId: string, queries: SearchQuery[]) => void;
}

export function SceneCard({
  scene,
  isFirst,
  isLast,
  onUpdate,
  onDelete,
  onMoveUp,
  onMoveDown,
  onOpenSplit,
  onMergeWithNext,
  onQueriesUpdated,
}: SceneCardProps) {
  const [title, setTitle] = useState(scene.title || `Cena ${scene.position}`);
  const [narration, setNarration] = useState(scene.narration);
  const [visualIntent, setVisualIntent] = useState(scene.visual_intent || "");
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(true);

  const formatSeconds = (sec: number | null | undefined) => {
    if (sec === null || sec === undefined) return "00:00";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const duration = (
    (scene.end_estimate || 0) - (scene.start_estimate || 0)
  ).toFixed(1);

  const handleBlur = async () => {
    if (
      title === scene.title &&
      narration === scene.narration &&
      visualIntent === (scene.visual_intent || "")
    ) {
      return;
    }

    setIsSaving(true);
    try {
      await onUpdate(scene.id, {
        title: title.trim() || undefined,
        narration: narration.trim(),
        visual_intent: visualIntent.trim() || undefined,
      });
      setIsSaved(true);
    } catch (err) {
      console.error("Erro ao salvar cena:", err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-slate-900/70 border border-white/10 hover:border-blue-500/30 rounded-2xl p-5 space-y-4 transition-all shadow-lg">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/5 pb-3">
        <div className="flex items-center gap-3">
          <span className="px-2.5 py-1 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-mono font-bold">
            CENA {scene.position.toString().padStart(2, "0")}
          </span>

          <input
            type="text"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setIsSaved(false);
            }}
            onBlur={handleBlur}
            className="bg-transparent font-semibold text-sm text-white focus:outline-none focus:border-b focus:border-blue-500 transition-all min-w-[200px]"
            placeholder={`Cena ${scene.position}`}
          />
        </div>

        <div className="flex items-center gap-3">
          {/* Time Estimate Badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-950 border border-white/5 text-xs text-slate-400 font-mono">
            <Clock className="h-3 w-3 text-blue-400" />
            <span>
              {formatSeconds(scene.start_estimate)} → {formatSeconds(scene.end_estimate)}
            </span>
            <span className="text-slate-600">({duration}s)</span>
          </div>

          {/* Status Indicator */}
          {isSaving ? (
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Loader2 className="h-3 w-3 animate-spin" /> Salvando...
            </span>
          ) : isSaved ? (
            <span className="text-xs text-emerald-400 flex items-center gap-1">
              <Check className="h-3 w-3" /> Salvo
            </span>
          ) : (
            <span className="text-xs text-amber-400">• Não salvo</span>
          )}

          {/* Action buttons */}
          <div className="flex items-center gap-1 border-l border-white/10 pl-2">
            <button
              onClick={() => onMoveUp(scene.id)}
              disabled={isFirst}
              className="p-1 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/5 rounded-lg transition-colors"
              title="Mover para cima"
            >
              <ChevronUp className="h-4 w-4" />
            </button>
            <button
              onClick={() => onMoveDown(scene.id)}
              disabled={isLast}
              className="p-1 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/5 rounded-lg transition-colors"
              title="Mover para baixo"
            >
              <ChevronDown className="h-4 w-4" />
            </button>
            <button
              onClick={() => onOpenSplit(scene)}
              className="p-1 text-slate-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
              title="Dividir cena em duas"
            >
              <Scissors className="h-4 w-4" />
            </button>
            {!isLast && (
              <button
                onClick={() => onMergeWithNext(scene)}
                className="p-1 text-slate-400 hover:text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-colors"
                title="Unir com a próxima cena"
              >
                <Combine className="h-4 w-4" />
              </button>
            )}
            <button
              onClick={() => {
                if (confirm(`Excluir Cena ${scene.position}?`)) {
                  onDelete(scene.id);
                }
              }}
              className="p-1 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
              title="Excluir cena"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Narration Field */}
      <div className="space-y-1">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Narração / Texto Falado
        </label>
        <textarea
          rows={3}
          value={narration}
          onChange={(e) => {
            setNarration(e.target.value);
            setIsSaved(false);
          }}
          onBlur={handleBlur}
          className="w-full bg-slate-950/60 border border-white/5 hover:border-white/15 focus:border-blue-500 rounded-xl p-3 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none resize-none leading-relaxed transition-all"
        />
      </div>

      {/* Visual Intent Field */}
      <div className="space-y-1">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-blue-400">
          <Eye className="h-3.5 w-3.5" />
          <span>Intenção Visual / Direção de Arte</span>
        </div>
        <input
          type="text"
          value={visualIntent}
          onChange={(e) => {
            setVisualIntent(e.target.value);
            setIsSaved(false);
          }}
          onBlur={handleBlur}
          placeholder="Ex: B-roll de datacenter com luzes azuis ou tela azul da morte"
          className="w-full bg-slate-950/60 border border-white/5 hover:border-white/15 focus:border-blue-500 rounded-xl px-3.5 py-2 text-xs text-blue-200 placeholder:text-slate-600 focus:outline-none transition-all"
        />
      </div>

      {/* Queries Section */}
      <SceneQueriesSection
        sceneId={scene.id}
        initialQueries={scene.queries || []}
        onQueriesUpdated={(queries) => onQueriesUpdated?.(scene.id, queries)}
      />
    </div>
  );
}
