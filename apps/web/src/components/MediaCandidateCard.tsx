/* eslint-disable @next/next/no-img-element */
"use client";

import { useState } from "react";
import { MediaCandidate } from "@/types";
import { 
  ShieldCheck, 
  Film, 
  Image as ImageIcon, 
  ExternalLink, 
  Copy, 
  Check 
} from "lucide-react";

interface MediaCandidateCardProps {
  candidate: MediaCandidate;
}

export function MediaCandidateCard({ candidate }: MediaCandidateCardProps) {
  const [copied, setCopied] = useState(false);
  const isVideo = candidate.media_type === "VIDEO";

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(candidate.url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback
    }
  };

  const formatDuration = (sec?: number | null) => {
    if (!sec) return null;
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="group relative bg-slate-950/80 border border-white/10 hover:border-blue-500/40 rounded-2xl overflow-hidden shadow-lg transition-all flex flex-col justify-between">
      {/* Thumbnail Area */}
      <div className="relative aspect-video w-full bg-slate-900 overflow-hidden">
        {candidate.preview_url ? (
          <img
            src={candidate.preview_url}
            alt={candidate.title || "Mídia Pexels"}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-600">
            {isVideo ? <Film className="h-8 w-8" /> : <ImageIcon className="h-8 w-8" />}
          </div>
        )}

        {/* Top Badges overlay */}
        <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between gap-1.5 pointer-events-none">
          {/* Media Type & Duration */}
          <div className="flex items-center gap-1 px-2 py-0.5 rounded-lg bg-black/70 backdrop-blur text-[10px] font-mono text-white border border-white/10">
            {isVideo ? <Film className="h-3 w-3 text-blue-400" /> : <ImageIcon className="h-3 w-3 text-indigo-400" />}
            <span>{isVideo ? "Vídeo" : "Foto"}</span>
            {isVideo && candidate.duration && (
              <span className="text-slate-400 font-semibold">• {formatDuration(candidate.duration)}</span>
            )}
          </div>

          {/* Legal Rights Badge */}
          <div
            className="flex items-center gap-1 px-2 py-0.5 rounded-lg bg-emerald-950/80 backdrop-blur border border-emerald-500/30 text-emerald-300 text-[10px] font-semibold font-mono"
            title="Licença Pexels: Livre para uso comercial, sem necessidade de atribuição obrigatória."
          >
            <ShieldCheck className="h-3 w-3 text-emerald-400" />
            <span>SAFE_REUSE</span>
          </div>
        </div>

        {/* Hover Action Overlay */}
        <div className="absolute inset-0 bg-black/50 backdrop-blur-xs opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
          <a
            href={candidate.url}
            target="_blank"
            rel="noreferrer"
            className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-all backdrop-blur"
            title="Ver no Pexels"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
          <button
            onClick={handleCopyLink}
            className="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white transition-all backdrop-blur"
            title="Copiar URL"
          >
            {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Info Content Area */}
      <div className="p-3.5 space-y-2 text-xs">
        <div className="flex items-start justify-between gap-2">
          <p className="font-semibold text-slate-200 line-clamp-1 flex-1" title={candidate.title || ""}>
            {candidate.title || `Mídia ${candidate.external_id}`}
          </p>
          {candidate.width && candidate.height && (
            <span className="text-[10px] font-mono text-slate-500 shrink-0">
              {candidate.width}x{candidate.height}
            </span>
          )}
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-white/5">
          <span className="truncate">Por {candidate.author || "Pexels Creator"}</span>
          <span className="text-[10px] uppercase font-mono text-slate-500 font-semibold shrink-0">
            Pexels
          </span>
        </div>
      </div>
    </div>
  );
}
