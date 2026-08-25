"use client";

import { useState, useEffect } from "react";
import { MediaCandidate } from "@/types";
import { listSceneCandidates, searchSceneMedia } from "@/lib/api-client";
import { MediaCandidateCard } from "@/components/MediaCandidateCard";
import { 
  Sparkles, 
  Film, 
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
  const [filter, setFilter] = useState<"ALL" | "PEXELS" | "WIKIMEDIA" | "IMAGE" | "VIDEO">("ALL");
  const [selectedProvider, setSelectedProvider] = useState<string>("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-fetch candidates when sceneId changes
  useEffect(() => {
    let isMounted = true;
    async function loadCandidates() {
      try {
        const data = await listSceneCandidates(sceneId);
        if (isMounted) {
          setCandidates(data);
        }
      } catch {
        // Silently keep current state if load fails
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
      const provParam = selectedProvider === "all" ? undefined : selectedProvider;
      const results = await searchSceneMedia(sceneId, provParam, 4);
      setCandidates(results);
    } catch (err: any) {
      setError(err?.message || "Erro ao buscar mídias.");
    } finally {
      setLoading(false);
    }
  };

  const filteredCandidates = candidates.filter((c) => {
    if (filter === "PEXELS") return c.provider.toLowerCase() === "pexels";
    if (filter === "WIKIMEDIA") return c.provider.toLowerCase() === "wikimedia";
    if (filter === "IMAGE") return c.media_type === "IMAGE";
    if (filter === "VIDEO") return c.media_type === "VIDEO";
    return true;
  });

  const pexelsCount = candidates.filter((c) => c.provider.toLowerCase() === "pexels").length;
  const wikiCount = candidates.filter((c) => c.provider.toLowerCase() === "wikimedia").length;
  const photoCount = candidates.filter((c) => c.media_type === "IMAGE").length;
  const videoCount = candidates.filter((c) => c.media_type === "VIDEO").length;

  return (
    <div className="pt-3 border-t border-white/5 space-y-4">
      {/* Header toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Film className="h-3.5 w-3.5 text-blue-400" />
            <span>Mídias & Procedência ({candidates.length})</span>
          </span>

          {candidates.length > 0 && (
            <div className="flex flex-wrap items-center gap-1 bg-slate-950 p-0.5 rounded-lg border border-white/5 text-[11px]">
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
              {pexelsCount > 0 && (
                <button
                  type="button"
                  onClick={() => setFilter("PEXELS")}
                  className={`px-2 py-0.5 rounded-md transition-all ${
                    filter === "PEXELS"
                      ? "bg-emerald-600 text-white font-medium shadow-xs"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Pexels ({pexelsCount})
                </button>
              )}
              {wikiCount > 0 && (
                <button
                  type="button"
                  onClick={() => setFilter("WIKIMEDIA")}
                  className={`px-2 py-0.5 rounded-md transition-all ${
                    filter === "WIKIMEDIA"
                      ? "bg-indigo-600 text-white font-medium shadow-xs"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Wikimedia ({wikiCount})
                </button>
              )}
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
              {videoCount > 0 && (
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
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="bg-slate-950 border border-white/10 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="all">Todos os Provedores (Pexels + Wikimedia)</option>
            <option value="pexels">Apenas Pexels (B-Roll)</option>
            <option value="wikimedia">Apenas Wikimedia (Histórico / Oficial)</option>
          </select>

          <button
            type="button"
            onClick={handleSearch}
            disabled={loading || !hasQueries}
            className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Sparkles className="h-3.5 w-3.5" />
            )}
            <span>{candidates.length > 0 ? "Atualizar Busca" : "Buscar Mídias"}</span>
          </button>
        </div>
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
            Nenhuma mídia associada a esta cena ainda. Use o seletor acima para buscar fotos e vídeos no Pexels e no Wikimedia Commons.
          </p>
        </div>
      ) : filteredCandidates.length === 0 ? (
        <p className="text-xs text-slate-400 italic py-2 text-center">
          Nenhuma mídia do filtro selecionado encontrada.
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
