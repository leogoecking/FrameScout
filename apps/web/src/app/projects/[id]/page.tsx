"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Project, Scene, VisualPlanExport, ProjectFidelityMetrics } from "@/types";
import { 
  getProject, 
  listScenes, 
  updateProject, 
  exportProjectVisualPlan,
  getProjectFidelityMetrics
} from "@/lib/api-client";
import { ScriptEditor } from "@/components/ScriptEditor";
import { SceneList } from "@/components/SceneList";
import { VisualTimeline } from "@/components/VisualTimeline";
import { VideoStudioPlayer } from "@/components/VideoStudioPlayer";
import { VisualPlanExportModal } from "@/components/VisualPlanExportModal";
import { 
  ArrowLeft, 
  FileEdit, 
  Layers, 
  Film, 
  Download, 
  Loader2, 
  AlertCircle,
  Play
} from "lucide-react";

export default function ProjectWorkspacePage() {
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [fidelityMetrics, setFidelityMetrics] = useState<ProjectFidelityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"SCRIPT" | "SCENES" | "TIMELINE" | "STUDIO">("SCENES");

  // Export Modal state
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [planData, setPlanData] = useState<VisualPlanExport | null>(null);
  const [exportLoading, setExportLoading] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const [projData, scenesData, metricsData] = await Promise.all([
          getProject(projectId),
          listScenes(projectId),
          getProjectFidelityMetrics(projectId).catch(() => null),
        ]);
        setProject(projData);
        setScenes(scenesData);
        setFidelityMetrics(metricsData);
      } catch (err: any) {
        setError(err.message || "Erro ao carregar projeto.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [projectId]);

  const refreshMetrics = async () => {
    try {
      const metricsData = await getProjectFidelityMetrics(projectId);
      setFidelityMetrics(metricsData);
    } catch {
      // Keep existing state
    }
  };

  const handleSaveScript = async (newScript: string) => {
    if (!project) return;
    const updated = await updateProject(project.id, { script_raw: newScript });
    setProject(updated);
    refreshMetrics();
  };

  const handleOpenExportModal = async () => {
    setExportLoading(true);
    try {
      const plan = await exportProjectVisualPlan(projectId);
      setPlanData(plan);
      setExportModalOpen(true);
    } catch (err: any) {
      alert(err?.message || "Erro ao gerar o plano de exportação.");
    } finally {
      setExportLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-20 flex flex-col items-center justify-center space-y-4">
        <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
        <p className="text-slate-400 text-sm">Carregando workspace do projeto...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-20 space-y-4">
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error || "Projeto não encontrado."}</span>
        </div>
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Voltar para Projetos</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 animate-fade-in">
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div className="space-y-1">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors mb-1"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Painel de Projetos</span>
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white">{project.name}</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-mono">
              {project.language}
            </span>
            {fidelityMetrics && fidelityMetrics.scenes_covered > 0 && (
              <span
                className={`px-2.5 py-0.5 rounded-full border text-xs font-mono font-bold flex items-center gap-1 shadow-xs ${
                  fidelityMetrics.average_fidelity >= 80
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                    : fidelityMetrics.average_fidelity >= 50
                    ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                    : "bg-slate-800 text-slate-300 border-slate-700"
                }`}
                title={`Fidelidade média do projeto: ${fidelityMetrics.average_fidelity}%. ${fidelityMetrics.high_fidelity_count} cenas com alta fidelidade (≥80%), ${fidelityMetrics.broll_count} com B-Roll.`}
              >
                <span>Fidelidade: {fidelityMetrics.average_fidelity}%</span>
                <span className="text-[10px] text-slate-400 font-normal">
                  ({fidelityMetrics.scenes_covered}/{fidelityMetrics.total_scenes} cenas)
                </span>
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setActiveTab("STUDIO")}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all cursor-pointer"
          >
            <Play className="h-3.5 w-3.5 fill-white" />
            <span>Studio de Vídeo</span>
          </button>

          <button
            type="button"
            onClick={handleOpenExportModal}
            disabled={exportLoading}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10 font-semibold text-xs flex items-center gap-2 transition-all cursor-pointer disabled:opacity-50"
          >
            {exportLoading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Download className="h-3.5 w-3.5" />
            )}
            <span>Exportar Plano</span>
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex items-center gap-2 border-b border-white/10 pb-px">
        <button
          type="button"
          onClick={() => setActiveTab("SCRIPT")}
          className={`px-4 py-2.5 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            activeTab === "SCRIPT"
              ? "border-blue-500 text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <FileEdit className="h-4 w-4" />
          <span>1. Roteiro & Narração</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("SCENES")}
          className={`px-4 py-2.5 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            activeTab === "SCENES"
              ? "border-blue-500 text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Layers className="h-4 w-4" />
          <span>2. Quadro de Cenas & Mídias</span>
          <span className="px-1.5 py-0.5 rounded-full bg-white/10 text-[10px] font-mono">
            {scenes.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("TIMELINE")}
          className={`px-4 py-2.5 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            activeTab === "TIMELINE"
              ? "border-blue-500 text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Film className="h-4 w-4" />
          <span>3. Linha do Tempo Visual</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("STUDIO")}
          className={`px-4 py-2.5 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            activeTab === "STUDIO"
              ? "border-emerald-500 text-white bg-emerald-500/5 rounded-t-lg"
              : "border-transparent text-emerald-400 hover:text-emerald-300"
          }`}
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          <span>4. Studio de Vídeo (.MP4)</span>
        </button>
      </div>

      {/* Workspace Active View */}
      {activeTab === "SCRIPT" && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">Editor de Roteiro</h2>
              <p className="text-xs text-slate-400">
                Escreva ou cole seu roteiro completo. Cada quebra de linha dupla gerará uma nova cena cronológica.
              </p>
            </div>
          </div>
          <ScriptEditor
            initialScript={project.script_raw || ""}
            projectId={project.id}
            onSave={handleSaveScript}
          />
        </div>
      )}

      {activeTab === "SCENES" && (
        <div className="space-y-6">
          <SceneList
            projectId={project.id}
            hasScript={Boolean(project.script_raw && project.script_raw.trim().length > 0)}
            initialScenes={scenes}
            onScenesUpdated={(updatedScenes) => {
              setScenes(updatedScenes);
              refreshMetrics();
            }}
            onAssetSelected={refreshMetrics}
          />
        </div>
      )}

      {activeTab === "TIMELINE" && (
        <div className="space-y-6">
          <VisualTimeline
            projectId={project.id}
            onNavigateToScenes={() => setActiveTab("SCENES")}
            onOpenExportModal={handleOpenExportModal}
          />
        </div>
      )}

      {activeTab === "STUDIO" && (
        <div className="space-y-6">
          <VideoStudioPlayer
            projectId={project.id}
            projectName={project.name}
            totalScenes={scenes.length}
          />
        </div>
      )}

      {/* Export Modal */}
      {planData && (
        <VisualPlanExportModal
          isOpen={exportModalOpen}
          onClose={() => setExportModalOpen(false)}
          plan={planData}
        />
      )}
    </div>
  );
}
