"use client";

import { useState, useEffect } from "react";
import { ExtractedEntity, SearchQuery, SearchQueryCreate, SearchQueryUpdate } from "@/types";
import { 
  createQuery, 
  deleteQuery, 
  extractSceneEntities, 
  generateSceneQueries, 
  updateQuery 
} from "@/lib/api-client";
import { QueryBadge } from "@/components/QueryBadge";
import { QueryEditorModal } from "@/components/QueryEditorModal";
import { 
  Sparkles, 
  Plus, 
  Search, 
  Loader2, 
  Tag, 
  Building2, 
  Rocket, 
  User, 
  Cpu, 
  MapPin, 
  Calendar, 
  Zap,
  PlusCircle
} from "lucide-react";

interface SceneQueriesSectionProps {
  sceneId: string;
  initialQueries?: SearchQuery[];
  onQueriesUpdated?: (queries: SearchQuery[]) => void;
}

const CATEGORY_CONFIG: Record<string, { label: string; bg: string; text: string; border: string; icon: any }> = {
  ORGANIZATION: {
    label: "Org",
    bg: "bg-emerald-500/10",
    text: "text-emerald-300",
    border: "border-emerald-500/30",
    icon: Building2,
  },
  PRODUCT: {
    label: "Produto",
    bg: "bg-indigo-500/10",
    text: "text-indigo-300",
    border: "border-indigo-500/30",
    icon: Rocket,
  },
  PERSON: {
    label: "Pessoa",
    bg: "bg-blue-500/10",
    text: "text-blue-300",
    border: "border-blue-500/30",
    icon: User,
  },
  TECHNOLOGY: {
    label: "Tech",
    bg: "bg-sky-500/10",
    text: "text-sky-300",
    border: "border-sky-500/30",
    icon: Cpu,
  },
  LOCATION: {
    label: "Local",
    bg: "bg-amber-500/10",
    text: "text-amber-300",
    border: "border-amber-500/30",
    icon: MapPin,
  },
  DATE_TIME: {
    label: "Data",
    bg: "bg-rose-500/10",
    text: "text-rose-300",
    border: "border-rose-500/30",
    icon: Calendar,
  },
  EVENT: {
    label: "Evento",
    bg: "bg-orange-500/10",
    text: "text-orange-300",
    border: "border-orange-500/30",
    icon: Zap,
  },
};

export function SceneQueriesSection({
  sceneId,
  initialQueries = [],
  onQueriesUpdated,
}: SceneQueriesSectionProps) {
  const [queries, setQueries] = useState<SearchQuery[]>(initialQueries);
  const [entities, setEntities] = useState<ExtractedEntity[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExtractingEntities, setIsExtractingEntities] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [queryToEdit, setQueryToEdit] = useState<SearchQuery | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Synchronize when parent updates initialQueries (e.g. batch generation)
  useEffect(() => {
    setQueries(initialQueries);
  }, [initialQueries]);

  const notify = (newQueries: SearchQuery[]) => {
    setQueries(newQueries);
    if (onQueriesUpdated) {
      onQueriesUpdated(newQueries);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const generated = await generateSceneQueries(sceneId);
      notify(generated);
    } catch (err: any) {
      setError(err?.message || "Erro ao gerar queries.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExtractEntities = async () => {
    setIsExtractingEntities(true);
    setError(null);
    try {
      const res = await extractSceneEntities(sceneId);
      setEntities(res.entities || []);
    } catch (err: any) {
      setError(err?.message || "Erro ao extrair entidades da cena.");
    } finally {
      setIsExtractingEntities(false);
    }
  };

  const handleAddEntityAsQuery = async (entity: ExtractedEntity) => {
    try {
      const created = await createQuery(sceneId, {
        query: `${entity.text} ${entity.category === "ORGANIZATION" ? "official" : "broll"}`,
        priority: 2,
      });
      notify([...queries, created]);
    } catch (err: any) {
      setError(err?.message || "Erro ao adicionar query de entidade.");
    }
  };

  const handleSaveModal = async (data: SearchQueryCreate | SearchQueryUpdate) => {
    if (queryToEdit) {
      const updated = await updateQuery(queryToEdit.id, data);
      notify(queries.map((q) => (q.id === queryToEdit.id ? updated : q)));
    } else {
      const created = await createQuery(sceneId, data as SearchQueryCreate);
      notify([...queries, created]);
    }
  };

  const handleDelete = async (queryId: string) => {
    try {
      await deleteQuery(queryId);
      notify(queries.filter((q) => q.id !== queryId));
    } catch (err: any) {
      setError(err?.message || "Erro ao excluir query.");
    }
  };

  return (
    <div className="pt-3 border-t border-white/5 space-y-3">
      {/* Header & Main Actions */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400">
            <Search className="h-3.5 w-3.5 text-indigo-400" />
            <span>Consultas de Busca ({queries.length})</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleExtractEntities}
            disabled={isExtractingEntities}
            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-teal-300 text-[11px] font-medium flex items-center gap-1 border border-teal-500/20 transition-all disabled:opacity-50"
            title="Detectar entidades nomeadas (NER) na narração desta cena"
          >
            {isExtractingEntities ? (
              <Loader2 className="h-3 w-3 animate-spin text-teal-400" />
            ) : (
              <Tag className="h-3 w-3 text-teal-400" />
            )}
            <span>Extrair Entidades</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setQueryToEdit(null);
              setIsModalOpen(true);
            }}
            className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-medium flex items-center gap-1 border border-white/5 transition-all"
          >
            <Plus className="h-3 w-3" />
            <span>Adicionar</span>
          </button>

          <button
            type="button"
            onClick={handleGenerate}
            disabled={isGenerating}
            className="px-2.5 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-[11px] font-medium flex items-center gap-1 transition-all disabled:opacity-50"
          >
            {isGenerating ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <Sparkles className="h-3 w-3" />
            )}
            <span>{queries.length > 0 ? "Regerar Queries" : "Gerar Queries"}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="text-xs text-red-400 bg-red-500/10 p-2 rounded-lg border border-red-500/20">
          {error}
        </div>
      )}

      {/* Extracted Entities Section (NER Chips) */}
      {entities.length > 0 && (
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-white/5 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-medium text-slate-400">
            <span className="flex items-center gap-1.5 text-teal-400">
              <Tag className="h-3 w-3" />
              <span>Entidades Detectadas ({entities.length}):</span>
            </span>
            <span className="text-[10px] text-slate-500">Clique em + para adicionar como busca</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {entities.map((ent, idx) => {
              const cfg = CATEGORY_CONFIG[ent.category] || CATEGORY_CONFIG.TECHNOLOGY;
              const IconComp = cfg.icon;
              return (
                <div
                  key={`${ent.text}-${idx}`}
                  className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md border text-[11px] ${cfg.bg} ${cfg.text} ${cfg.border}`}
                >
                  <IconComp className="h-3 w-3 shrink-0 opacity-80" />
                  <span className="font-medium">{ent.text}</span>
                  <span className="text-[9px] uppercase opacity-60 font-mono">[{cfg.label}]</span>
                  <button
                    type="button"
                    onClick={() => handleAddEntityAsQuery(ent)}
                    className="ml-0.5 hover:text-white transition-colors"
                    title={`Criar query de busca para ${ent.text}`}
                  >
                    <PlusCircle className="h-3 w-3" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Query Badges Container */}
      {queries.length === 0 ? (
        <p className="text-xs text-slate-400 italic py-1">
          Nenhuma consulta de busca gerada ainda. Clique em &quot;Gerar Queries&quot; ou &quot;Extrair Entidades&quot; para criar buscas automáticas para esta cena.
        </p>
      ) : (
        <div className="flex flex-wrap gap-2 pt-1">
          {queries.map((q) => (
            <QueryBadge
              key={q.id}
              query={q}
              onDelete={handleDelete}
              onEdit={(query) => {
                setQueryToEdit(query);
                setIsModalOpen(true);
              }}
            />
          ))}
        </div>
      )}

      {/* Modal */}
      <QueryEditorModal
        queryToEdit={queryToEdit}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setQueryToEdit(null);
        }}
        onSave={handleSaveModal}
      />
    </div>
  );
}

