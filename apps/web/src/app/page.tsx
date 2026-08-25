"use client";

import { useEffect, useState } from "react";
import { HealthData, Project } from "@/types";
import { fetchHealth, listProjects, deleteProject } from "@/lib/api-client";
import { ProjectCard } from "@/components/ProjectCard";
import { CreateProjectModal } from "@/components/CreateProjectModal";
import { 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  Search, 
  ShieldCheck, 
  Download, 
  Server, 
  Database, 
  Cpu, 
  FileText,
  Plus,
  Film,
  Sparkles,
  FolderOpen
} from "lucide-react";

export default function HomePage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const loadProjects = async () => {
    setProjectsLoading(true);
    try {
      const data = await listProjects();
      setProjects(data);
    } catch (err) {
      console.error("Erro ao carregar projetos:", err);
    } finally {
      setProjectsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data))
      .finally(() => setLoading(false));

    loadProjects();
  }, []);

  const handleProjectCreated = (newProject: Project) => {
    setProjects((prev) => [newProject, ...prev]);
  };

  const handleDeleteProject = async (id: string) => {
    try {
      await deleteProject(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      alert("Erro ao excluir projeto.");
    }
  };

  const pipelineSteps = [
    { title: "1. Roteiro", desc: "Estruturação textual e marcações", icon: FileText },
    { title: "2. Cenas", desc: "Segmentação e intenção visual", icon: Layers },
    { title: "3. Queries", desc: "Fatos, entidades e B-roll", icon: Search },
    { title: "4. Providers", desc: "Pexels & Wikimedia Commons", icon: Cpu },
    { title: "5. Direitos", desc: "RightsStatus e procedência", icon: ShieldCheck },
    { title: "6. Exportação", desc: "Pacote organizado + manifest", icon: Download },
  ];

  return (
    <div className="max-w-7xl mx-auto px-6 py-12 space-y-12">
      {/* Hero & Quick Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-mono">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Sprint 1 — Projects & Scripts</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Do roteiro à mídia certa.
          </h1>
          <p className="text-base text-slate-400 max-w-2xl leading-relaxed">
            Crie projetos, cole roteiros, divida em cenas e descubra mídias com classificação jurídica
            e de fidelidade factual rigorosa.
          </p>
        </div>

        <div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-5 py-3 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm flex items-center gap-2 shadow-xl shadow-blue-600/25 hover:scale-105 transition-all"
          >
            <Plus className="h-4 w-4" />
            <span>Novo Projeto</span>
          </button>
        </div>
      </div>

      {/* Projects Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Film className="h-5 w-5 text-blue-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">Meus Projetos</h2>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-white/5 font-mono">
              {projects.length}
            </span>
          </div>
        </div>

        {projectsLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-48 bg-slate-900/40 border border-white/5 rounded-2xl animate-pulse" />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div className="glass-panel p-12 rounded-3xl text-center space-y-4 border-dashed border-white/10">
            <div className="inline-flex p-4 rounded-2xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <FolderOpen className="h-8 w-8" />
            </div>
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-white">Nenhum projeto encontrado</h3>
              <p className="text-sm text-slate-400 max-w-md mx-auto">
                Comece criando seu primeiro projeto para colar seu roteiro de vídeo e planejar a pesquisa visual.
              </p>
            </div>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Criar Primeiro Projeto</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onDelete={handleDeleteProject}
              />
            ))}
          </div>
        )}
      </div>

      {/* System Status Dashboard */}
      <div className="glass-panel p-6 rounded-2xl glow-effect space-y-6">
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <Server className="h-5 w-5 text-blue-400" />
            <h2 className="font-semibold text-base text-white">Status da Infraestrutura & Banco de Dados</h2>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {loading ? "Verificando..." : `Atualizado em: ${new Date().toLocaleTimeString()}`}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Frontend */}
          <div className="bg-slate-900/60 border border-white/5 p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">Frontend (Next.js)</span>
              <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="h-3 w-3" /> Online
              </span>
            </div>
            <p className="text-xs text-slate-500">Next.js 14 App Router • Tailwind CSS • TypeScript</p>
          </div>

          {/* Backend API */}
          <div className="bg-slate-900/60 border border-white/5 p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">API Backend (FastAPI)</span>
              {loading ? (
                <span className="text-xs text-slate-400">Checando...</span>
              ) : health?.status === "ok" ? (
                <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="h-3 w-3" /> Conectado ({health.version})
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  <AlertTriangle className="h-3 w-3" /> {health?.status || "Inativo"}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500">FastAPI • SQLAlchemy 2.0 Async • Pydantic v2</p>
          </div>

          {/* PostgreSQL Database */}
          <div className="bg-slate-900/60 border border-white/5 p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">Banco (PostgreSQL)</span>
              {loading ? (
                <span className="text-xs text-slate-400">Checando...</span>
              ) : health?.database === "connected" ? (
                <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <Database className="h-3 w-3" /> Conectado
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
                  <AlertTriangle className="h-3 w-3" /> Desconectado
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500">PostgreSQL 16 • Migrations • UUID Schema</p>
          </div>
        </div>
      </div>

      {/* Architecture Pipeline Map */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white tracking-tight">Pipeline de Processamento do FrameScout</h2>
          <span className="text-xs font-mono text-slate-500">ROADMAP SPRINT 1 → 10</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {pipelineSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={idx}
                className="bg-slate-900/40 border border-white/5 p-4 rounded-xl space-y-3 hover:border-blue-500/30 transition-all group"
              >
                <div className="h-8 w-8 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-sm text-slate-200">{step.title}</h3>
                  <p className="text-xs text-slate-500 mt-1 leading-snug">{step.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Create Project Modal */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreated={handleProjectCreated}
      />
    </div>
  );
}
