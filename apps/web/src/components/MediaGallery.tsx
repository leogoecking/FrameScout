"use client";

import { useState, useEffect } from "react";
import { MediaCandidate } from "@/types";
import { listSceneCandidates, searchSceneMedia } from "@/lib/api-client";
import { MediaCandidateCard } from "@/components/MediaCandidateCard";
import { 
  Sparkles, 
  Film, 
  Image as ImageIcon, 
  Grid, 
  Loader2, 
  AlertCircle,
  FolderOpen
} from "lucide-react";

interface MediaGalleryProps {
  sceneId: string;
  hasQueries: boolean;
  initialCandidates?: MediaCandidate[];
}

export function MediaGallery({
  sceneId,
  hasQueries,
  initialCandidates = [],
}: MediaGalleryProps) {
  const [candidates, setCandidates] = useState<MediaCandidate[]>(initialCandidates);
  const [filter, setFilter] = useState<"ALL" | "IMAGE" | "VIDEO">("ALL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-fetch candidates when sceneId changes or if initially empty
  useEffect(() => {
    let isMounted = true;
    async function loadCandidates() {
      try {
        const data = await listSceneCandidates(sceneId);
        if (isMounted) {
          setCandidates(data);
        }
      } catch {
        // Silently keep current state if initial load fails
      }
    }
    loadCandidates();
    return () => {
      isMounted = false;
    };
  }, [sceneId]);

  const handleSearch = async () => {
    if (!hasQueries) {
      setError("Gere pelo menos uma query de busca antes de pesquisar mídias.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const results = await searchSceneMedia(sceneId, 4);
      setCandidates(results);
    } catch (err: any) {
      setError(err?.message || "Erro ao buscar mídias no Pexels.");
    } finally {
      setLoading(false);
    }
  };

  const filteredCandidates = candidates.filter((c) => {
    if (filter === "IMAGE") return c.media_type === "IMAGE";
    if (filter === "VIDEO") return c.media_type === "VIDEO";
    return true;
  });

  const photoCount = candidates.filter((c) => c.media_type === "IMAGE").length;
  const videoCount = candidates.filter((c) => c.media_type === "VIDEO").length;

  return (
    <div className="pt-3 border-t border-white/5 space-y-4">
      {/* Header toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Film className="h-3.5 w-3.5 text-blue-400" />
            <span>Candidatos de Mídia ({candidates.length})</span>
          </span>

          {candidates.length > 0 && (
            <div className="flex items-center gap-1 bg-slate-950 p-0.5 rounded-lg border border-white/5 text-[11px]">
              <button
                type="button"
                onClick={() => setFilter("ALL")}
                className={`px-2 py-0.5 rounded-md transition-all ${
                  filter === "ALL"
                    ? "bg-blue-600 text-white font-medium shadow-xs"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Todos ({candidates.length})
              </button>
              <button
                type="button"
                onClick={() => setFilter("IMAGE")}
                className={`px-2 py-0.5 rounded-md transition-all ${
                  filter === "IMAGE"
                    ? "bg-blue-600 text-white font-medium shadow-xs"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Fotos ({photoCount})
              </button>
              <button
                type="button"
                onClick={() => setFilter("VIDEO")}
                className={`px-2 py-0.5 rounded-md transition-all ${
                  filter === "VIDEO"
                    ? "bg-blue-600 text-white font-medium shadow-xs"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Vídeos ({videoCount})
              </button>
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={handleSearch}
          disabled={loading || !hasQueries}
          className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {loading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Sparkles className="h-3.5 w-3.5" />
          )}
          <span>{candidates.length > 0 ? "Atualizar Busca Pexels" : "Buscar Mídia no Pexels"}</span>
        </button>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Media Candidates Grid */}
      {candidates.length === 0 ? (
        <div className="bg-slate-950/40 rounded-xl p-6 text-center space-y-2 border border-dashed border-white/5">
          <FolderOpen className="h-6 w-6 text-slate-500 mx-auto" />
          <p className="text-xs text-slate-400">
            Nenhuma mídia associada a esta cena ainda. Clique em &quot;Buscar Mídia no Pexels&quot; para consultar o acervo aberto.
          </p>
        </div>
      ) : filteredCandidates.length === 0 ? (
        <p className="text-xs text-slate-400 italic py-2 text-center">
          Nenhuma mídia do tipo selecionado encontrada.
        </p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {filteredCandidates.map((candidate) => (
            <MediaCandidateCard key={candidate.id} candidate={candidate} />
          ))}
        </div>
      )}
    </div>
  );
}
