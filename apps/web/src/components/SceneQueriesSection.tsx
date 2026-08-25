"use client";

import { useState } from "react";
import { SearchQuery, SearchQueryCreate, SearchQueryUpdate } from "@/types";
import { 
  createQuery, 
  deleteQuery, 
  generateSceneQueries, 
  updateQuery 
} from "@/lib/api-client";
import { QueryBadge } from "@/components/QueryBadge";
import { QueryEditorModal } from "@/components/QueryEditorModal";
import { Sparkles, Plus, Search, Loader2 } from "lucide-react";

interface SceneQueriesSectionProps {
  sceneId: string;
  initialQueries?: SearchQuery[];
  onQueriesUpdated?: (queries: SearchQuery[]) => void;
}

export function SceneQueriesSection({
  sceneId,
  initialQueries = [],
  onQueriesUpdated,
}: SceneQueriesSectionProps) {
  const [queries, setQueries] = useState<SearchQuery[]>(initialQueries);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [queryToEdit, setQueryToEdit] = useState<SearchQuery | null>(null);
  const [error, setError] = useState<string | null>(null);

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

      {/* Query Badges Container */}
      {queries.length === 0 ? (
        <p className="text-xs text-slate-400 italic py-1">
          Nenhuma consulta de busca gerada ainda. Clique em &quot;Gerar Queries&quot; para criar buscas automáticas para esta cena.
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
