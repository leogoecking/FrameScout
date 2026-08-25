"use client";

import { useState, useEffect } from "react";
import { MediaCandidate, SelectedAsset } from "@/types";
import { 
  listSceneCandidates, 
  searchSceneMedia, 
  listSceneSelectedAssets, 
  selectAssetForScene, 
  removeSelectedAsset,
  rerankSceneCandidates
} from "@/lib/api-client";
import { MediaCandidateCard } from "@/components/MediaCandidateCard";
import { 
  Sparkles, 
  Film, 
  Loader2, 
  AlertCircle,
  FolderOpen,
  RefreshCw,
  SlidersHorizontal
} from "lucide-react";

interface MediaGalleryProps {
  sceneId: string;
  hasQueries: boolean;
  initialCandidates?: MediaCandidate[];
  onAssetSelected?: () => void;
}

export function MediaGallery({
  sceneId,
  hasQueries,
  initialCandidates = [],
  onAssetSelected,
}: MediaGalleryProps) {
  const [candidates, setCandidates] = useState<MediaCandidate[]>(initialCandidates);
  const [selectedAsset, setSelectedAsset] = useState<SelectedAsset | null>(null);
  const [filter, setFilter] = useState<"ALL" | "PEXELS" | "WIKIMEDIA" | "OPENVERSE" | "NASA" | "IMAGE" | "VIDEO">("ALL");
  const [fidelityFilter, setFidelityFilter] = useState<"ALL" | "HIGH" | "BROLL">("ALL");
  const [selectedProvider, setSelectedProvider] = useState<string>("all");
  const [loading, setLoading] = useState(false);
  const [reranking, setReranking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-fetch candidates and selected assets when sceneId changes
  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        const [candsData, assetsData] = await Promise.all([
          listSceneCandidates(sceneId),
          listSceneSelectedAssets(sceneId),
        ]);
        if (isMounted) {
          setCandidates(candsData);
          setSelectedAsset(assetsData.length > 0 ? assetsData[0] : null);
        }
      } catch {
        // Silently keep current state if load fails
      }
    }
    loadData();
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
    setFilter("ALL");
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

  const handleRerank = async () => {
    setReranking(true);
    setError(null);
    try {
      const results = await rerankSceneCandidates(sceneId);
      setCandidates(results);
    } catch (err: any) {
      setError(err?.message || "Erro ao recalcular fidelidade semântica.");
    } finally {
      setReranking(false);
    }
  };

  const handleSelectAsset = async (candidateId: string, framingMode: string) => {
    try {
      const res = await selectAssetForScene(sceneId, {
        media_candidate_id: candidateId,
        framing_mode: framingMode,
      });
      setSelectedAsset(res);
      if (onAssetSelected) onAssetSelected();
    } catch (err: any) {
      setError(err?.message || "Erro ao fixar mídia na cena.");
    }
  };

  const handleDeselectAsset = async () => {
    if (!selectedAsset) return;
    try {
      await removeSelectedAsset(selectedAsset.id);
      setSelectedAsset(null);
      if (onAssetSelected) onAssetSelected();
    } catch (err: any) {
      setError(err?.message || "Erro ao remover mídia da cena.");
    }
  };

  const filteredCandidates = candidates.filter((c) => {
    // Provider & Type filter
    if (filter === "PEXELS" && c.provider.toLowerCase() !== "pexels") return false;
    if (filter === "WIKIMEDIA" && c.provider.toLowerCase() !== "wikimedia") return false;
    if (filter === "OPENVERSE" && c.provider.toLowerCase() !== "openverse") return false;
    if (filter === "NASA" && c.provider.toLowerCase() !== "nasa") return false;
    if (filter === "IMAGE" && c.media_type !== "IMAGE") return false;
    if (filter === "VIDEO" && c.media_type !== "VIDEO") return false;

    // Fidelity filter (Sprint 11/12)
    const score = c.fidelity_score !== null && c.fidelity_score !== undefined
      ? Math.round(c.fidelity_score * 100)
      : 75;
    if (fidelityFilter === "HIGH" && score < 80) return false;
    if (fidelityFilter === "BROLL" && (score < 50 || score >= 80)) return false;

    return true;
  });

  const pexelsCount = candidates.filter((c) => c.provider.toLowerCase() === "pexels").length;
  const wikiCount = candidates.filter((c) => c.provider.toLowerCase() === "wikimedia").length;
  const openverseCount = candidates.filter((c) => c.provider.toLowerCase() === "openverse").length;
  const nasaCount = candidates.filter((c) => c.provider.toLowerCase() === "nasa").length;
  const photoCount = candidates.filter((c) => c.media_type === "IMAGE").length;
  const videoCount = candidates.filter((c) => c.media_type === "VIDEO").length;

  return (
    <div className="pt-3 border-t border-white/5 space-y-4">
      {/* Header toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Film className="h-3.5 w-3.5 text-blue-400" />
            <span>Mídias & Fidelidade ({candidates.length})</span>
          </span>

          {candidates.length > 0 && (
            <div className="flex flex-wrap items-center gap-1 bg-slate-950 p-0.5 rounded-lg border border-white/5 text-[11px]">
              <button
                type="button"
                onClick={() => setFilter("ALL")}
                className={`px-2 py-0.5 rounded-md transition-all cursor-pointer ${
                  filter === "ALL"
                    ? "bg-blue-600 text-white font-medium shadow-xs"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Todos ({candidates.length})
              </button>
              {nasaCount > 0 && (
                <button
                  type="button"
                  onClick={() => setFilter("NASA")}
                  className={`px-2 py-0.5 rounded-md transition-all cursor-pointer ${
                    filter === "NASA"
                      ? "bg-sky-600 text-white font-medium shadow-xs"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  NASA ({nasaCount})
                </button>
              )}
              {openverseCount > 0 && (
                <button
                  type="button"
                  onClick={() => setFilter("OPENVERSE")}
                  className={`px-2 py-0.5 rounded-md transition-all cursor-pointer ${
                    filter === "OPENVERSE"
                      ? "bg-purple-600 text-white font-medium shadow-xs"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Openverse ({openverseCount})
                </button>
              )}
              {wikiCount > 0 && (
                <button
                  type="button"
                  onClick={() => setFilter("WIKIMEDIA")}
                  className={`px-2 py-0.5 rounded-md transition-all cursor-pointer ${
                    filter === "WIKIMEDIA"
                      ? "bg-indigo-600 text-white font-medium shadow-xs"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Wikimedia ({wikiCount})
                </button>
              )}
              {pexelsCount > 0 && (
                <button
                  type="button"
                  onClick={() => setFilter("PEXELS")}
                  className={`px-2 py-0.5 rounded-md transition-all cursor-pointer ${
                    filter === "PEXELS"
                      ? "bg-emerald-600 text-white font-medium shadow-xs"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  Pexels ({pexelsCount})
                </button>
              )}
              <button
                type="button"
                onClick={() => setFilter("IMAGE")}
                className={`px-2 py-0.5 rounded-md transition-all cursor-pointer ${
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
                  className={`px-2 py-0.5 rounded-md transition-all cursor-pointer ${
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

          {/* Fidelity Filter Selector */}
          {candidates.length > 0 && (
            <div className="flex items-center gap-1 bg-slate-950 p-0.5 rounded-lg border border-white/5 text-[11px]">
              <span className="text-[10px] text-slate-500 px-1.5 font-mono flex items-center gap-1">
                <SlidersHorizontal className="h-3 w-3" />
                <span>Score:</span>
              </span>
              <button
                type="button"
                onClick={() => setFidelityFilter("ALL")}
                className={`px-1.5 py-0.5 rounded text-[10px] font-mono transition-all cursor-pointer ${
                  fidelityFilter === "ALL" ? "bg-white/20 text-white font-bold" : "text-slate-400 hover:text-white"
                }`}
              >
                Todos
              </button>
              <button
                type="button"
                onClick={() => setFidelityFilter("HIGH")}
                className={`px-1.5 py-0.5 rounded text-[10px] font-mono transition-all cursor-pointer ${
                  fidelityFilter === "HIGH" ? "bg-emerald-600 text-white font-bold" : "text-emerald-400/70 hover:text-emerald-300"
                }`}
              >
                ≥80% Alta
              </button>
              <button
                type="button"
                onClick={() => setFidelityFilter("BROLL")}
                className={`px-1.5 py-0.5 rounded text-[10px] font-mono transition-all cursor-pointer ${
                  fidelityFilter === "BROLL" ? "bg-amber-600 text-white font-bold" : "text-amber-400/70 hover:text-amber-300"
                }`}
              >
                50-79% B-Roll
              </button>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {candidates.length > 0 && (
            <button
              type="button"
              onClick={handleRerank}
              disabled={reranking}
              className="px-2.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 hover:text-white text-xs font-medium flex items-center gap-1.5 border border-white/10 transition-all cursor-pointer"
              title="Recalcular pontuações de fidelidade semântica com o roteiro atual"
            >
              <RefreshCw className={`h-3 w-3 ${reranking ? "animate-spin text-blue-400" : ""}`} />
              <span>{reranking ? "Reavaliando..." : "Reavaliar"}</span>
            </button>
          )}

          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="bg-slate-950 border border-white/10 rounded-xl px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="all">Todas as Fontes (Openverse, NASA, Wiki, Pexels)</option>
            <option value="openverse">Apenas Openverse (+700M Imagens Abertas)</option>
            <option value="nasa">Apenas NASA (Missões, Espaço & Vídeos)</option>
            <option value="wikimedia">Apenas Wikimedia (Histórico / Oficial)</option>
            <option value="pexels">Apenas Pexels (Estoque B-Roll)</option>
          </select>

          <button
            type="button"
            onClick={handleSearch}
            disabled={loading || !hasQueries}
            className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all cursor-pointer"
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
          {filteredCandidates.map((candidate) => {
            const isSelected = selectedAsset?.media_candidate_id === candidate.id;
            return (
              <MediaCandidateCard
                key={candidate.id}
                candidate={candidate}
                isSelected={isSelected}
                currentFramingMode={isSelected ? selectedAsset?.framing_mode : "FILL"}
                onSelect={handleSelectAsset}
                onDeselect={handleDeselectAsset}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}
