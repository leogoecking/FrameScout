/* eslint-disable @next/next/no-img-element */
"use client";

import { useState, useEffect, useCallback } from "react";
import { VisualPlanExport, RightsStatus } from "@/types";
import { exportProjectVisualPlan } from "@/lib/api-client";
import { 
  Clock, 
  Film, 
  Sparkles, 
  ShieldCheck, 
  AlertCircle, 
  HelpCircle, 
  ExternalLink, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle,
  FileText,
  Maximize2,
  Image as ImageIcon
} from "lucide-react";

interface VisualTimelineProps {
  projectId: string;
  onNavigateToScenes?: () => void;
  onOpenExportModal?: () => void;
}

const rightsBadgeStyles: Record<
  RightsStatus,
  { label: string; bg: string; text: string; border: string; icon: any }
> = {
  SAFE_REUSE: {
    label: "SAFE_REUSE",
    bg: "bg-emerald-950/80",
    text: "text-emerald-300",
    border: "border-emerald-500/30",
    icon: ShieldCheck,
  },
  ATTRIBUTION_REQUIRED: {
    label: "ATRIBUIÇÃO OBRIGATÓRIA",
    bg: "bg-amber-950/80",
    text: "text-amber-300",
    border: "border-amber-500/30",
    icon: AlertCircle,
  },
  REVIEW_REQUIRED: {
    label: "REVISÃO NECESSÁRIA",
    bg: "bg-purple-950/80",
    text: "text-purple-300",
    border: "border-purple-500/30",
    icon: HelpCircle,
  },
  REFERENCE_ONLY: {
    label: "APENAS REFERÊNCIA",
    bg: "bg-blue-950/80",
    text: "text-blue-300",
    border: "border-blue-500/30",
    icon: HelpCircle,
  },
  BLOCKED: {
    label: "BLOQUEADO",
    bg: "bg-red-950/80",
    text: "text-red-300",
    border: "border-red-500/30",
    icon: AlertTriangle,
  },
};

export function VisualTimeline({
  projectId,
  onNavigateToScenes,
  onOpenExportModal,
}: VisualTimelineProps) {
  const [plan, setPlan] = useState<VisualPlanExport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imgErrors, setImgErrors] = useState<Record<number, boolean>>({});

  const loadPlan = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await exportProjectVisualPlan(projectId);
      setPlan(data);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar o plano da linha do tempo.");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadPlan();
  }, [loadPlan]);

  const handleImgError = (scenePos: number) => {
    setImgErrors((prev) => ({ ...prev, [scenePos]: true }));
  };

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="h-8 w-8 text-blue-500 animate-spin" />
        <p className="text-sm text-slate-400">Compilando linha do tempo visual...</p>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error || "Não foi possível carregar a linha do tempo."}</span>
        </div>
        <button
          type="button"
          onClick={loadPlan}
          className="px-3 py-1.5 rounded-xl bg-red-500/20 hover:bg-red-500/30 text-white font-medium text-xs cursor-pointer"
        >
          Tentar Novamente
        </button>
      </div>
    );
  }

  const mins = Math.floor(plan.total_duration_seconds / 60);
  const secs = Math.floor(plan.total_duration_seconds % 60);
  const coveragePercent =
    plan.total_scenes > 0
      ? Math.round((plan.covered_scenes_count / plan.total_scenes) * 100)
      : 0;

  return (
    <div className="space-y-6">
      {/* Header Stats Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Total Duration */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/10 backdrop-blur flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              Duração Estimada Total
            </span>
            <p className="text-2xl font-bold font-mono text-white">
              {mins.toString().padStart(2, "0")}:{secs.toString().padStart(2, "0")}
            </p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center border border-blue-500/20">
            <Clock className="h-5 w-5" />
          </div>
        </div>

        {/* Media Coverage */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/10 backdrop-blur flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
              Cobertura Visual
            </span>
            <p className="text-2xl font-bold font-mono text-white">
              {plan.covered_scenes_count}/{plan.total_scenes}{" "}
              <span className="text-sm font-normal text-slate-400">({coveragePercent}%)</span>
            </p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
            <CheckCircle2 className="h-5 w-5" />
          </div>
        </div>

        {/* Export Action Card */}
        <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-900/40 via-indigo-900/40 to-slate-900/60 border border-blue-500/30 backdrop-blur flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-mono text-blue-300 uppercase tracking-wider">
              Plano de Produção
            </span>
            <p className="text-sm font-medium text-slate-200">
              {plan.consolidated_attributions.length} crédito(s) legais
            </p>
          </div>
          <button
            type="button"
            onClick={onOpenExportModal}
            className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-blue-600/30 transition-all cursor-pointer"
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Exportar Plano</span>
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-white/5">
        <div
          className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-500 transition-all duration-500"
          style={{ width: `${coveragePercent}%` }}
        />
      </div>

      {/* Timeline Scenes List */}
      <div className="space-y-4">
        {plan.scenes.map((scene) => {
          const mStart = Math.floor(scene.start_estimate / 60);
          const sStart = Math.floor(scene.start_estimate % 60);
          const mEnd = Math.floor(scene.end_estimate / 60);
          const sEnd = Math.floor(scene.end_estimate % 60);
          const timecode = `${mStart.toString().padStart(2, "0")}:${sStart
            .toString()
            .padStart(2, "0")} ➔ ${mEnd.toString().padStart(2, "0")}:${sEnd
            .toString()
            .padStart(2, "0")}`;

          const asset = scene.selected_asset;
          const candidate = asset?.media_candidate;
          const statusConfig = candidate
            ? rightsBadgeStyles[candidate.rights_status] || rightsBadgeStyles.REVIEW_REQUIRED
            : null;
          const StatusIcon = statusConfig?.icon;
          const isImgBroken = imgErrors[scene.scene_position];

          return (
            <div
              key={scene.scene_position}
              className="p-5 rounded-2xl bg-slate-900/60 border border-white/10 hover:border-white/20 transition-all backdrop-blur flex flex-col md:flex-row items-stretch gap-5"
            >
              {/* Left Column: Scene Info & Narration */}
              <div className="flex-1 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="h-6 w-6 rounded-full bg-blue-500/20 text-blue-400 text-xs font-mono font-bold flex items-center justify-center border border-blue-500/30">
                      {scene.scene_position}
                    </span>
                    <h3 className="font-semibold text-slate-100 text-base">{scene.scene_title}</h3>
                  </div>

                  <span className="px-2.5 py-0.5 rounded-lg bg-black/60 border border-white/10 text-xs font-mono text-slate-300 flex items-center gap-1">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span>{timecode} ({scene.duration.toFixed(1)}s)</span>
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-black/40 border border-white/5 space-y-1.5">
                  <p className="text-xs text-slate-400 font-mono uppercase tracking-wider">Narração</p>
                  <p className="text-sm text-slate-200 leading-relaxed italic">
                    &quot;{scene.narration}&quot;
                  </p>
                </div>

                {scene.visual_intent && (
                  <div className="flex items-start gap-1.5 text-xs text-slate-400">
                    <Sparkles className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                    <span>Direção: {scene.visual_intent}</span>
                  </div>
                )}
              </div>

              {/* Right Column: Selected Media Preview */}
              <div className="w-full md:w-80 shrink-0 flex flex-col justify-between rounded-xl bg-slate-950/80 border border-white/10 overflow-hidden">
                {candidate ? (
                  <div className="flex flex-col h-full justify-between">
                    <div className="relative aspect-video w-full bg-slate-900 overflow-hidden">
                      {candidate.preview_url && !isImgBroken ? (
                        <img
                          src={candidate.preview_url}
                          alt={candidate.title || "Preview"}
                          onError={() => handleImgError(scene.scene_position)}
                          className={`w-full h-full ${
                            asset?.framing_mode === "FIT"
                              ? "object-contain bg-black"
                              : "object-cover"
                          }`}
                        />
                      ) : (
                        <div className="w-full h-full flex flex-col items-center justify-center text-slate-600 bg-slate-900 gap-1.5 p-4 text-center">
                          {candidate.media_type === "VIDEO" ? (
                            <Film className="h-7 w-7 text-slate-500" />
                          ) : (
                            <ImageIcon className="h-7 w-7 text-slate-500" />
                          )}
                          <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3 text-amber-500/70" /> Prévia indisponível
                          </span>
                        </div>
                      )}

                      <div className="absolute top-2 left-2 right-2 flex items-center justify-between pointer-events-none">
                        <span className="px-2 py-0.5 rounded-md bg-black/70 backdrop-blur text-[10px] font-mono text-white border border-white/10 flex items-center gap-1">
                          <Film className="h-3 w-3 text-blue-400" />
                          <span>{candidate.media_type}</span>
                        </span>

                        {statusConfig && StatusIcon && (
                          <span
                            className={`px-2 py-0.5 rounded-md border text-[10px] font-mono font-semibold flex items-center gap-1 ${statusConfig.bg} ${statusConfig.text} ${statusConfig.border}`}
                          >
                            <StatusIcon className="h-3 w-3" />
                            <span className="truncate max-w-[120px]">{statusConfig.label}</span>
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="p-3 space-y-2 text-xs">
                      <p className="font-semibold text-slate-200 truncate" title={candidate.title || ""}>
                        {candidate.title || candidate.external_id}
                      </p>

                      <div className="flex items-center justify-between text-[11px] text-slate-400">
                        <span className="flex items-center gap-1">
                          <Maximize2 className="h-3 w-3 text-indigo-400" />
                          <span className="font-mono">{asset?.framing_mode}</span>
                        </span>
                        <a
                          href={candidate.url}
                          target="_blank"
                          rel="noreferrer"
                          className="hover:text-white flex items-center gap-0.5 text-blue-400"
                        >
                          <span>Ver Fonte</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-full min-h-[160px] p-4 flex flex-col items-center justify-center text-center space-y-2.5">
                    <AlertTriangle className="h-6 w-6 text-amber-400" />
                    <p className="text-xs text-slate-400">Nenhuma mídia fixada nesta cena.</p>
                    {onNavigateToScenes && (
                      <button
                        type="button"
                        onClick={onNavigateToScenes}
                        className="px-2.5 py-1 rounded-lg bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 border border-blue-500/30 text-xs font-semibold transition-all cursor-pointer"
                      >
                        Escolher Mídia
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
