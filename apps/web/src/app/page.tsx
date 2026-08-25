"use client";

import { useEffect, useState } from "react";
import { HealthData } from "@/types";
import { fetchHealth } from "@/lib/api-client";
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
  FileText 
} from "lucide-react";

export default function HomePage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data))
      .finally(() => setLoading(false));
  }, []);

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
      {/* Hero Section */}
      <div className="space-y-4">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
          Do roteiro à mídia certa — com procedência e confiança.
        </h1>
        <p className="text-lg text-slate-400 max-w-3xl leading-relaxed">
          FrameScout analisa roteiros de vídeo, divide em cenas, gera queries inteligentes e busca mídias
          classificadas rigorosamente por fidelidade e direitos de reutilização.
        </p>
      </div>

      {/* System Status Dashboard (Sprint 0 Foundation) */}
      <div className="glass-panel p-6 rounded-2xl glow-effect space-y-6">
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <Server className="h-5 w-5 text-blue-400" />
            <h2 className="font-semibold text-lg text-white">Status da Infraestrutura (Sprint 0)</h2>
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

      {/* RightsStatus Principles Highlight */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/30 via-indigo-950/20 to-slate-900/40 border border-blue-500/20 space-y-3">
        <div className="flex items-center gap-2 text-blue-400 font-semibold text-sm">
          <ShieldCheck className="h-5 w-5" />
          <span>Princípio Fundamental de Licenciamento</span>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed">
          O FrameScout não assume que o acesso técnico a um arquivo implica direito de reutilização.
          Toda mídia é classificada como <code className="text-emerald-400 font-mono text-xs">SAFE_REUSE</code>,{" "}
          <code className="text-blue-400 font-mono text-xs">ATTRIBUTION_REQUIRED</code>,{" "}
          <code className="text-amber-400 font-mono text-xs">REVIEW_REQUIRED</code>,{" "}
          <code className="text-purple-400 font-mono text-xs">REFERENCE_ONLY</code> ou{" "}
          <code className="text-red-400 font-mono text-xs">BLOCKED</code>.
        </p>
      </div>
    </div>
  );
}
