"use client";

import Link from "next/link";
import { Project } from "@/types";
import { 
  FileText, 
  ArrowRight, 
  Trash2, 
  Calendar, 
  Globe 
} from "lucide-react";

interface ProjectCardProps {
  project: Project;
  onDelete: (id: string) => void;
}

export function ProjectCard({ project, onDelete }: ProjectCardProps) {
  const languageNames: Record<string, string> = {
    "pt-BR": "Português",
    "en-US": "English",
    "es-ES": "Español",
  };

  const formattedDate = new Date(project.updated_at).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  const previewSnippet = project.script_raw
    ? project.script_raw.length > 120
      ? project.script_raw.substring(0, 120) + "..."
      : project.script_raw
    : "Nenhum roteiro adicionado ainda.";

  return (
    <div className="bg-slate-900/60 border border-white/10 hover:border-blue-500/40 rounded-2xl p-5 flex flex-col justify-between transition-all group relative overflow-hidden">
      <div className="space-y-3">
        {/* Top badges */}
        <div className="flex items-center justify-between">
          <span className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-white/5 font-mono">
            <Globe className="h-3 w-3 text-blue-400" />
            {languageNames[project.language] || project.language}
          </span>
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {formattedDate}
          </span>
        </div>

        {/* Project Title */}
        <div>
          <h3 className="font-semibold text-base text-white group-hover:text-blue-400 transition-colors line-clamp-1">
            {project.name}
          </h3>
          <p className="text-xs text-slate-400 mt-2 line-clamp-3 leading-relaxed">
            {previewSnippet}
          </p>
        </div>
      </div>

      {/* Footer / Actions */}
      <div className="pt-5 mt-4 border-t border-white/5 flex items-center justify-between">
        <button
          onClick={() => {
            if (confirm(`Deseja realmente excluir o projeto "${project.name}"?`)) {
              onDelete(project.id);
            }
          }}
          className="text-slate-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10 transition-colors"
          title="Excluir projeto"
        >
          <Trash2 className="h-4 w-4" />
        </button>

        <Link
          href={`/projects/${project.id}`}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600/10 hover:bg-blue-600 text-blue-400 hover:text-white border border-blue-500/20 text-xs font-medium transition-all"
        >
          <span>Abrir Workspace</span>
          <ArrowRight className="h-3 w-3" />
        </Link>
      </div>
    </div>
  );
}
