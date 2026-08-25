"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Project, ProjectUpdate, Scene } from "@/types";
import { getProject, updateProject, deleteProject, listScenes } from "@/lib/api-client";
import { ScriptEditor } from "@/components/ScriptEditor";
import { SceneList } from "@/components/SceneList";
import { 
  ArrowLeft, 
  Layers, 
  Trash2, 
  Search, 
  FileText, 
  Loader2, 
  Check, 
  AlertCircle,
  Sparkles
} from "lucide-react";

export default function ProjectWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"script" | "scenes">("script");

  // Edit metadata state
  const [name, setName] = useState("");
  const [language, setLanguage] = useState("pt-BR");
  const [isUpdatingMeta, setIsUpdatingMeta] = useState(false);
  const [metaSaved, setMetaSaved] = useState(true);

  useEffect(() => {
    if (!projectId) return;

    Promise.all([getProject(projectId), listScenes(projectId)])
      .then(([projData, scenesData]) => {
        setProject(projData);
        setName(projData.name);
        setLanguage(projData.language);
        setScenes(scenesData);
        // If scenes already exist, open scenes tab directly
        if (scenesData.length > 0) {
          setActiveTab("scenes");
        }
      })
      .catch((err) => setError(err?.message || "Não foi possível carregar o projeto."))
      .finally(() => setLoading(false));
  }, [projectId]);

  const handleUpdateMetadata = async () => {
    if (!project || !name.trim()) return;
    setIsUpdatingMeta(true);
    try {
      const payload: ProjectUpdate = { name: name.trim(), language };
      const updated = await updateProject(project.id, payload);
      setProject(updated);
      setMetaSaved(true);
    } catch (err: any) {
      setError(err?.message || "Erro ao atualizar informações do projeto.");
    } finally {
      setIsUpdatingMeta(false);
    }
  };

  const handleSaveScript = async (newScript: string) => {
    if (!project) return;
    const payload: ProjectUpdate = { script_raw: newScript };
    const updated = await updateProject(project.id, payload);
    setProject(updated);
  };

  const handleDelete = async () => {
    if (!project) return;
    if (confirm(`Tem certeza que deseja excluir o projeto "${project.name}"?`)) {
      try {
        await deleteProject(project.id);
        router.push("/");
      } catch (err: any) {
        alert(err?.message || "Erro ao excluir projeto.");
      }
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-24 flex flex-col items-center justify-center space-y-4">
        <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
        <p className="text-sm text-slate-400">Carregando workspace do projeto...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-24 space-y-4 text-center">
        <div className="inline-flex p-3 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
          <AlertCircle className="h-8 w-8" />
        </div>
        <h2 className="text-xl font-bold text-white">Projeto não encontrado</h2>
        <p className="text-sm text-slate-400">{error || "O projeto solicitado não existe ou foi removido."}</p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-sm transition-all"
        >
          <ArrowLeft className="h-4 w-4" /> Voltar ao Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Navigation Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Voltar ao Dashboard</span>
        </Link>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDelete}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-medium border border-red-500/20 transition-all"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Excluir Projeto</span>
          </button>
        </div>
      </div>

      {/* Project Header & Metadata Bar */}
      <div className="glass-panel p-6 rounded-2xl space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Editable Name */}
          <div className="flex-1 space-y-1">
            <label className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
              Nome do Projeto
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setMetaSaved(false);
              }}
              onBlur={handleUpdateMetadata}
              className="w-full bg-slate-950/60 border border-white/10 rounded-xl px-4 py-2 text-lg font-bold text-white focus:outline-none focus:border-blue-500 transition-all"
            />
          </div>

          {/* Language & Save status */}
          <div className="flex items-center gap-4">
            <div className="space-y-1">
              <label className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
                Idioma
              </label>
              <select
                value={language}
                onChange={(e) => {
                  setLanguage(e.target.value);
                  setMetaSaved(false);
                  setTimeout(handleUpdateMetadata, 100);
                }}
                className="bg-slate-950/60 border border-white/10 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 transition-all"
              >
                <option value="pt-BR">Português (Brasil)</option>
                <option value="en-US">English (US)</option>
                <option value="es-ES">Español</option>
              </select>
            </div>

            <div className="pt-5">
              {!metaSaved ? (
                <button
                  onClick={handleUpdateMetadata}
                  disabled={isUpdatingMeta}
                  className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium flex items-center gap-1.5 transition-all"
                >
                  {isUpdatingMeta ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
                  Salvar Info
                </button>
              ) : (
                <div className="px-3 py-2 text-xs text-emerald-400 flex items-center gap-1">
                  <Check className="h-3.5 w-3.5" />
                  Salvo
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-t border-white/10 pt-4">
          <button
            onClick={() => setActiveTab("script")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "script"
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                : "bg-slate-800/60 text-slate-400 hover:text-white hover:bg-slate-800"
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>1. Roteiro</span>
          </button>

          <button
            onClick={() => setActiveTab("scenes")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
              activeTab === "scenes"
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                : "bg-slate-800/60 text-slate-400 hover:text-white hover:bg-slate-800"
            }`}
          >
            <Layers className="h-4 w-4" />
            <span>2. Quadro de Cenas</span>
            <span className="px-1.5 py-0.2 rounded-full bg-white/10 text-[10px] font-mono">
              {scenes.length}
            </span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === "script" ? (
          <ScriptEditor
            initialScript={project.script_raw || ""}
            onSave={handleSaveScript}
          />
        ) : (
          <SceneList
            projectId={project.id}
            hasScript={Boolean(project.script_raw && project.script_raw.trim())}
            initialScenes={scenes}
            onScenesUpdated={(updatedScenes) => setScenes(updatedScenes)}
          />
        )}
      </div>

      {/* Next Step Teaser: Sprint 3 */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/40 via-indigo-950/30 to-slate-900/40 border border-blue-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            <Search className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">Próxima Etapa: Gerador de Queries (Sprint 3)</h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Transformar cada cena em buscas específicas categorizadas por fidelidade, fontes oficiais e B-roll.
            </p>
          </div>
        </div>

        <button
          disabled
          className="px-4 py-2 rounded-xl bg-slate-800 text-slate-500 text-xs font-medium cursor-not-allowed border border-white/5"
        >
          Gerar Queries (Sprint 3)
        </button>
      </div>
    </div>
  );
}
