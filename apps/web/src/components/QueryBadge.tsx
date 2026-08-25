"use client";

import { QueryType, SearchQuery } from "@/types";
import { Search, Shield, Building2, User, MapPin, Lightbulb, Film, X } from "lucide-react";

interface QueryBadgeProps {
  query: SearchQuery;
  onDelete?: (queryId: string) => void;
  onEdit?: (query: SearchQuery) => void;
}

const typeStyles: Record<
  QueryType,
  { label: string; bg: string; text: string; border: string; icon: any }
> = {
  OFFICIAL: {
    label: "Oficial",
    bg: "bg-purple-500/10",
    text: "text-purple-400",
    border: "border-purple-500/20",
    icon: Shield,
  },
  EVENT: {
    label: "Evento",
    bg: "bg-amber-500/10",
    text: "text-amber-400",
    border: "border-amber-500/20",
    icon: Search,
  },
  COMPANY: {
    label: "Empresa",
    bg: "bg-emerald-500/10",
    text: "text-emerald-400",
    border: "border-emerald-500/20",
    icon: Building2,
  },
  PERSON: {
    label: "Pessoa",
    bg: "bg-pink-500/10",
    text: "text-pink-400",
    border: "border-pink-500/20",
    icon: User,
  },
  LOCATION: {
    label: "Local",
    bg: "bg-orange-500/10",
    text: "text-orange-400",
    border: "border-orange-500/20",
    icon: MapPin,
  },
  CONCEPT: {
    label: "Conceito",
    bg: "bg-cyan-500/10",
    text: "text-cyan-400",
    border: "border-cyan-500/20",
    icon: Lightbulb,
  },
  BROLL: {
    label: "B-Roll",
    bg: "bg-blue-500/10",
    text: "text-blue-400",
    border: "border-blue-500/20",
    icon: Film,
  },
};

export function QueryBadge({ query, onDelete, onEdit }: QueryBadgeProps) {
  const config = typeStyles[query.query_type] || typeStyles.BROLL;
  const Icon = config.icon;

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs ${config.bg} ${config.text} ${config.border} shadow-sm group transition-all`}
    >
      <Icon className="h-3.5 w-3.5 shrink-0" />
      
      <span className="text-[10px] uppercase tracking-wider font-semibold font-mono opacity-80">
        {config.label}
      </span>

      <span
        onClick={() => onEdit?.(query)}
        className="font-medium text-slate-200 hover:text-white cursor-pointer select-none"
        title="Clique para editar busca"
      >
        &ldquo;{query.query}&rdquo;
      </span>

      <span className="px-1.5 py-0.5 rounded bg-black/40 text-[10px] font-mono text-slate-400" title={`Prioridade ${query.priority}`}>
        P{query.priority}
      </span>

      {onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(query.id);
          }}
          className="text-slate-400 hover:text-red-400 p-0.5 rounded transition-colors opacity-60 group-hover:opacity-100"
          title="Excluir busca"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}
