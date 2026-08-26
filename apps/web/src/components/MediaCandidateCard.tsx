/* eslint-disable @next/next/no-img-element */
"use client";

import { useState, useEffect } from "react";
import { MediaCandidate, RightsStatus } from "@/types";
import { 
  ShieldCheck, 
  AlertCircle, 
  HelpCircle, 
  Film, 
  Image as ImageIcon, 
  ExternalLink, 
  Copy, 
  Check, 
  AlertTriangle, 
  FileText,
  Pin,
  Maximize2,
  Sparkles,
  ChevronDown
} from "lucide-react";

interface MediaCandidateCardProps {
  candidate: MediaCandidate;
  isSelected?: boolean;
  currentFramingMode?: string;
  onSelect?: (candidateId: string, framingMode: string) => Promise<void>;
  onDeselect?: (candidateId: string) => Promise<void>;
}

const rightsBadgeStyles: Record<
  RightsStatus,
  { label: string; bg: string; text: string; border: string; icon: any; tooltip: string }
> = {
  SAFE_REUSE: {
    label: "SAFE_REUSE",
    bg: "bg-emerald-950/80",
    text: "text-emerald-300",
    border: "border-emerald-500/30",
    icon: ShieldCheck,
    tooltip: "Livre para uso comercial sem necessidade de atribuição obrigatória.",
  },
  ATTRIBUTION_REQUIRED: {
    label: "ATRIBUIÇÃO OBRIGATÓRIA",
    bg: "bg-amber-950/80",
    text: "text-amber-300",
    border: "border-amber-500/30",
    icon: AlertCircle,
    tooltip: "Requer citação de créditos e link de licença no vídeo final.",
  },
  REVIEW_REQUIRED: {
    label: "REVISÃO NECESSÁRIA",
    bg: "bg-purple-950/80",
    text: "text-purple-300",
    border: "border-purple-500/30",
    icon: HelpCircle,
    tooltip: "Uso restrito, marca registrada ou licença não verificada automaticamente.",
  },
  REFERENCE_ONLY: {
    label: "APENAS REFERÊNCIA",
    bg: "bg-blue-950/80",
    text: "text-blue-300",
    border: "border-blue-500/30",
    icon: HelpCircle,
    tooltip: "Material protegido. Utilize apenas como referência de direção de arte.",
  },
  BLOCKED: {
    label: "BLOQUEADO",
    bg: "bg-red-950/80",
    text: "text-red-300",
    border: "border-red-500/30",
    icon: AlertTriangle,
    tooltip: "Mídia com restrição jurídica ativa. Não utilizar.",
  },
};

export function MediaCandidateCard({
  candidate,
  isSelected = false,
  currentFramingMode = "FILL",
  onSelect,
  onDeselect,
}: MediaCandidateCardProps) {
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedCredit, setCopiedCredit] = useState(false);
  const [imgError, setImgError] = useState(false);
  const [framingMode, setFramingMode] = useState<string>(currentFramingMode);
  const [selecting, setSelecting] = useState(false);
  const [showFidelityDetails, setShowFidelityDetails] = useState(false);

  useEffect(() => {
    setFramingMode(currentFramingMode || "FILL");
  }, [currentFramingMode]);

  const isVideo = candidate.media_type === "VIDEO";
  const statusConfig =
    rightsBadgeStyles[candidate.rights_status] || rightsBadgeStyles.REVIEW_REQUIRED;
  const StatusIcon = statusConfig.icon;

  const fidelity = candidate.fidelity_score !== null && candidate.fidelity_score !== undefined
    ? Math.round(candidate.fidelity_score * 100)
    : 75;

  const fidelityBreakdown = candidate.metadata_json?.fidelity_breakdown;

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(candidate.url);
      setCopiedUrl(true);
      setTimeout(() => setCopiedUrl(false), 2500);
    } catch {
      // Fallback
    }
  };

  const handleCopyCredit = async () => {
    try {
      const creditLine =
        candidate.attribution ||
        `Mídia por ${candidate.author || "Autor"} via ${candidate.provider}`;
      await navigator.clipboard.writeText(creditLine);
      setCopiedCredit(true);
      setTimeout(() => setCopiedCredit(false), 2500);
    } catch {
      // Fallback
    }
  };

  const handleToggleSelect = async () => {
    setSelecting(true);
    try {
      if (isSelected && onDeselect) {
        await onDeselect(candidate.id);
      } else if (onSelect) {
        await onSelect(candidate.id, framingMode);
      }
    } finally {
      setSelecting(false);
    }
  };

  const handleFramingChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newMode = e.target.value;
    setFramingMode(newMode);
    if (isSelected && onSelect) {
      setSelecting(true);
      try {
        await onSelect(candidate.id, newMode);
      } finally {
        setSelecting(false);
      }
    }
  };

  const formatDuration = (sec?: number | null) => {
    if (!sec) return null;
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div
      className={`group relative bg-slate-950/80 rounded-2xl overflow-hidden shadow-lg transition-all flex flex-col justify-between border ${
        isSelected
          ? "border-emerald-500 ring-2 ring-emerald-500/20 shadow-emerald-950/50"
          : "border-white/10 hover:border-blue-500/40"
      }`}
    >
      {/* Thumbnail Area */}
      <div className="relative aspect-video w-full bg-slate-900 overflow-hidden">
        {candidate.preview_url && !imgError ? (
          <img
            src={candidate.preview_url}
            alt={candidate.title || "Mídia"}
            onError={() => setImgError(true)}
            className={`w-full h-full group-hover:scale-105 transition-transform duration-300 ${
              framingMode === "FIT" ? "object-contain bg-black/80" : "object-cover"
            }`}
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-slate-600 bg-slate-900 gap-1.5 p-4 text-center">
            {isVideo ? (
              <Film className="h-8 w-8 text-slate-500" />
            ) : (
              <ImageIcon className="h-8 w-8 text-slate-500" />
            )}
            <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
              <AlertTriangle className="h-3 w-3 text-amber-500/70" /> Prévia indisponível
            </span>
          </div>
        )}

        {/* Top Badges overlay */}
        <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between gap-1.5 pointer-events-none">
          {/* Media Type & Duration */}
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-lg bg-black/70 backdrop-blur text-[10px] font-mono text-white border border-white/10">
            {isVideo ? (
              <Film className="h-3 w-3 text-blue-400" />
            ) : (
              <ImageIcon className="h-3 w-3 text-indigo-400" />
            )}
            <span>{isVideo ? "Vídeo" : "Foto"}</span>
            {isVideo && candidate.duration && (
              <span className="text-slate-400 font-semibold">
                • {formatDuration(candidate.duration)}
              </span>
            )}
          </div>

          {/* Fidelity Score Badge (Sprint 11/12) */}
          <div
            onClick={(e) => {
              e.stopPropagation();
              setShowFidelityDetails(!showFidelityDetails);
            }}
            className={`pointer-events-auto cursor-pointer px-2 py-0.5 rounded-lg backdrop-blur border text-[10px] font-mono font-bold flex items-center gap-1 shadow transition-all ${
              fidelity >= 80
                ? "bg-emerald-950/80 text-emerald-300 border-emerald-500/40 hover:bg-emerald-900/80"
                : fidelity >= 50
                ? "bg-amber-950/80 text-amber-300 border-amber-500/40 hover:bg-amber-900/80"
                : "bg-slate-900/80 text-slate-300 border-slate-600/40 hover:bg-slate-800/80"
            }`}
            title="Clique para ver o detalhamento da pontuação de fidelidade"
          >
            <Sparkles className="h-3 w-3 shrink-0" />
            <span>{fidelity}% Fidelidade</span>
            <ChevronDown className={`h-2.5 w-2.5 transition-transform ${showFidelityDetails ? "rotate-180" : ""}`} />
          </div>
        </div>

        {/* Selected Banner */}
        {isSelected && (
          <div className="absolute bottom-2.5 left-2.5 flex items-center gap-1 px-2 py-0.5 rounded-lg bg-emerald-600 text-white text-[10px] font-semibold shadow-md">
            <Pin className="h-3 w-3" />
            <span>Mídia Fixada na Cena</span>
          </div>
        )}

        {/* Hover Action Overlay */}
        <div className="absolute inset-0 bg-black/50 backdrop-blur-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <a
            href={candidate.url}
            target="_blank"
            rel="noreferrer"
            className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-all backdrop-blur cursor-pointer"
            title="Ver na fonte oficial"
          >
            <ExternalLink className="h-4 w-4" />
          </a>

          <button
            type="button"
            onClick={handleCopyLink}
            className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-all backdrop-blur cursor-pointer"
            title="Copiar URL"
          >
            {copiedUrl ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
          </button>

          {candidate.rights_status === "ATTRIBUTION_REQUIRED" && (
            <button
              type="button"
              onClick={handleCopyCredit}
              className="px-2.5 py-2 rounded-xl bg-amber-600/30 hover:bg-amber-600/50 text-amber-300 border border-amber-500/40 text-[11px] font-medium flex items-center gap-1 transition-all backdrop-blur cursor-pointer"
              title="Copiar texto de atribuição obrigatória"
            >
              {copiedCredit ? (
                <Check className="h-3.5 w-3.5 text-emerald-400" />
              ) : (
                <FileText className="h-3.5 w-3.5" />
              )}
              <span>{copiedCredit ? "Copiado!" : "Copiar Crédito"}</span>
            </button>
          )}
        </div>
      </div>

      {/* Fidelity Score Breakdown Popover */}
      {showFidelityDetails && (
        <div className="p-3 bg-slate-900 border-b border-white/10 text-[11px] space-y-1.5 animate-fade-in">
          <div className="flex items-center justify-between text-slate-300 font-semibold border-b border-white/10 pb-1">
            <span>Avaliação de Fidelidade</span>
            <span className="font-mono text-emerald-400">{fidelity}/100</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5 text-slate-400 font-mono text-[10px]">
            <div>• Semântica: <span className="text-white">{Number(fidelityBreakdown?.semantic ?? (fidelity * 0.4)).toFixed(1)}/40</span></div>
            <div>• Entidades: <span className="text-white">{Number(fidelityBreakdown?.entities ?? (fidelity * 0.25)).toFixed(1)}/25</span></div>
            <div>• Autoridade: <span className="text-white">{Number(fidelityBreakdown?.authority ?? 14.0).toFixed(1)}/15</span></div>
            <div>• Contexto: <span className="text-white">{Number(fidelityBreakdown?.temporal ?? 10.0).toFixed(1)}/10</span></div>
            <div>• Resolução: <span className="text-white">{Number(fidelityBreakdown?.quality ?? 10.0).toFixed(1)}/10</span></div>
          </div>
        </div>
      )}

      {/* Info Content Area */}
      <div className="p-3.5 space-y-2.5 text-xs">
        <div className="flex items-start justify-between gap-2">
          <p
            className="font-semibold text-slate-200 line-clamp-1 flex-1"
            title={candidate.title || ""}
          >
            {candidate.title || `Mídia ${candidate.external_id}`}
          </p>
          {candidate.width && candidate.height && (
            <span className="text-[10px] font-mono text-slate-500 shrink-0">
              {candidate.width}x{candidate.height}
            </span>
          )}
        </div>

        {/* Legal Rights Badge */}
        <div
          className={`flex items-center gap-1 px-2 py-0.5 rounded-lg backdrop-blur border text-[10px] font-semibold font-mono w-fit ${statusConfig.bg} ${statusConfig.text} ${statusConfig.border}`}
          title={statusConfig.tooltip}
        >
          <StatusIcon className="h-3 w-3 shrink-0" />
          <span className="truncate max-w-[180px]">{statusConfig.label}</span>
        </div>

        {/* License Name */}
        {candidate.license && (
          <p className="text-[10px] text-slate-400 truncate" title={candidate.license}>
            Licença: <span className="text-slate-300 font-mono">{candidate.license}</span>
          </p>
        )}

        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-white/5">
          <span className="truncate">Por {candidate.author || "Autor Desconhecido"}</span>
          <span
            className={`text-[10px] uppercase font-mono font-semibold shrink-0 px-1.5 py-0.5 rounded ${
              (candidate.provider || "").toLowerCase() === "gemini"
                ? "bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/30 font-bold"
                : (candidate.provider || "").toLowerCase() === "nasa"
                ? "bg-sky-500/10 text-sky-400 border border-sky-500/20"
                : (candidate.provider || "").toLowerCase() === "openverse"
                ? "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                : (candidate.provider || "").toLowerCase() === "wikimedia"
                ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
            }`}
          >
            {(candidate.provider || "").toLowerCase() === "gemini"
              ? "✨ Gemini IA"
              : (candidate.provider || "").toLowerCase() === "nasa"
              ? "NASA"
              : (candidate.provider || "").toLowerCase() === "openverse"
              ? "Openverse"
              : (candidate.provider || "").toLowerCase() === "wikimedia"
              ? "Wikimedia"
              : "Pexels"}
          </span>
        </div>

        {/* Selection & Framing Controls */}
        {(onSelect || onDeselect) && (
          <div className="pt-2 border-t border-white/5 flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5">
              <Maximize2 className="h-3 w-3 text-slate-400" />
              <select
                value={framingMode}
                onChange={handleFramingChange}
                className="bg-slate-900 border border-white/10 rounded-lg px-2 py-1 text-[11px] text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="FILL">Preencher (FILL 16:9)</option>
                <option value="FIT">Ajustar (FIT)</option>
                <option value="PAN_AND_ZOOM">Ken Burns (PAN & ZOOM)</option>
              </select>
            </div>

            <button
              type="button"
              onClick={handleToggleSelect}
              disabled={selecting}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold flex items-center gap-1 transition-all cursor-pointer ${
                isSelected
                  ? "bg-emerald-600/20 hover:bg-red-600/20 text-emerald-400 hover:text-red-400 border border-emerald-500/30 hover:border-red-500/30"
                  : "bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20"
              }`}
            >
              <Pin className="h-3 w-3" />
              <span>{isSelected ? "Fixado" : "Fixar na Cena"}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
