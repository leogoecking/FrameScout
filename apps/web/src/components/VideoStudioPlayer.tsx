"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { RenderJob, VoiceOption } from "@/types";
import { 
  listAvailableVoices, 
  triggerRenderJob, 
  listProjectRenderJobs, 
  getRenderJob,
  getRenderVideoStreamUrl 
} from "@/lib/api-client";
import { 
  Play, 
  Download, 
  Sparkles, 
  Clock, 
  Mic, 
  Layers, 
  Film, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  RefreshCw, 
  Smartphone, 
  Monitor,
  ShieldCheck,
  AlertTriangle
} from "lucide-react";

interface VideoStudioPlayerProps {
  projectId: string;
  projectName: string;
  totalScenes: number;
}

export function VideoStudioPlayer({
  projectId,
  projectName,
  totalScenes,
}: VideoStudioPlayerProps) {
  const [voices, setVoices] = useState<VoiceOption[]>([]);
  const [selectedVoice, setSelectedVoice] = useState("pt-BR-AntonioNeural");
  const [aspectRatio, setAspectRatio] = useState<"16:9" | "9:16">("16:9");
  const [includeSubtitles, setIncludeSubtitles] = useState(true);
  const [includeCreditsCard, setIncludeCreditsCard] = useState(true);

  const [activeJob, setActiveJob] = useState<RenderJob | null>(null);
  const [jobsHistory, setJobsHistory] = useState<RenderJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [voicesList, jobsList] = await Promise.all([
        listAvailableVoices().catch(() => [
          { id: "pt-BR-AntonioNeural", name: "Antonio (Masculino, Natural)" },
          { id: "pt-BR-FranciscaNeural", name: "Francisca (Feminino, Expressivo)" },
          { id: "pt-BR-ThalitaNeural", name: "Thalita (Feminino, Jovem)" },
        ]),
        listProjectRenderJobs(projectId).catch(() => []),
      ]);
      setVoices(voicesList);
      setJobsHistory(jobsList);
      if (jobsList.length > 0) {
        setActiveJob(jobsList[0]);
      }
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar dados do Studio.");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Polling active render job
  useEffect(() => {
    if (!activeJob) return;

    const isRunning =
      activeJob.status === "PENDING" ||
      activeJob.status === "SYNTHESIZING_AUDIO" ||
      activeJob.status === "PROCESSING_MEDIA" ||
      activeJob.status === "RENDERING_VIDEO";

    if (isRunning) {
      pollingRef.current = setInterval(async () => {
        try {
          const updated = await getRenderJob(activeJob.id);
          setActiveJob(updated);
          if (updated.status === "COMPLETED" || updated.status === "FAILED") {
            if (pollingRef.current) clearInterval(pollingRef.current);
            const allJobs = await listProjectRenderJobs(projectId);
            setJobsHistory(allJobs);
          }
        } catch {
          // Keep polling
        }
      }, 2000);
    }

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [activeJob, projectId]);

  const handleStartRender = async () => {
    setIsStarting(true);
    setError(null);
    try {
      const job = await triggerRenderJob(projectId, {
        aspect_ratio: aspectRatio,
        voice: selectedVoice,
        include_subtitles: includeSubtitles,
        include_credits_card: includeCreditsCard,
      });
      setActiveJob(job);
      setJobsHistory((prev) => [job, ...prev]);
    } catch (err: any) {
      setError(err?.message || "Erro ao iniciar a renderização do vídeo.");
    } finally {
      setIsStarting(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="h-8 w-8 text-blue-500 animate-spin" />
        <p className="text-sm text-slate-400">Carregando FrameScout Studio Engine...</p>
      </div>
    );
  }

  const isRendering =
    activeJob &&
    (activeJob.status === "PENDING" ||
      activeJob.status === "SYNTHESIZING_AUDIO" ||
      activeJob.status === "PROCESSING_MEDIA" ||
      activeJob.status === "RENDERING_VIDEO");

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Studio Header Bar */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-blue-950/60 via-indigo-950/50 to-slate-900/60 border border-blue-500/20 backdrop-blur flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-mono font-bold flex items-center gap-1">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Studio Engine</span>
            </span>
            <span className="text-xs text-slate-400 font-mono">• Full HD 1080p</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            Motor de Montagem e Renderização de Vídeo
          </h2>
          <p className="text-xs text-slate-400 max-w-2xl">
            Sintetize a narração em áudio neural, anime fotos com movimento Ken Burns, processe vídeos e gere o arquivo final MP4 com créditos legais consolidados.
          </p>
        </div>

        <button
          type="button"
          onClick={handleStartRender}
          disabled={isStarting || Boolean(isRendering) || totalScenes === 0}
          className="px-5 py-3 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-bold text-sm flex items-center gap-2.5 shadow-xl shadow-blue-600/30 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
        >
          {isStarting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : isRendering ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4 fill-white" />
          )}
          <span>{isRendering ? "Renderizando..." : "🎬 Renderizar Vídeo Final (.MP4)"}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Studio Grid: Video Player + Settings Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Player & Active Render Pipeline (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="rounded-3xl bg-slate-950 border border-white/10 overflow-hidden shadow-2xl">
            {/* Player Header */}
            <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-slate-900/50">
              <div className="flex items-center gap-2">
                <Film className="h-4 w-4 text-blue-400" />
                <span className="font-semibold text-white text-sm">Visualizador de Produção</span>
              </div>

              {activeJob?.status === "COMPLETED" && (
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-mono font-medium flex items-center gap-1">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Pronto ({activeJob.duration_seconds}s)</span>
                </span>
              )}

              {activeJob?.status === "FAILED" && (
                <span className="px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 text-xs font-mono font-medium flex items-center gap-1">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  <span>Falha na renderização</span>
                </span>
              )}
            </div>

            {/* Video Canvas or Progress State */}
            <div className="relative aspect-video w-full bg-black flex items-center justify-center overflow-hidden">
              {activeJob?.status === "COMPLETED" && activeJob.video_url ? (
                <video
                  src={getRenderVideoStreamUrl(activeJob.id)}
                  controls
                  className="w-full h-full object-contain"
                  poster=""
                />
              ) : isRendering ? (
                <div className="p-8 flex flex-col items-center justify-center text-center space-y-4 max-w-md">
                  <RefreshCw className="h-10 w-10 text-blue-500 animate-spin" />
                  <div className="space-y-1">
                    <p className="text-base font-bold text-white">
                      {activeJob?.status === "SYNTHESIZING_AUDIO" && "1/3. Sintetizando Narração Neural..."}
                      {activeJob?.status === "PROCESSING_MEDIA" && "2/3. Processando Mídias & Ken Burns..."}
                      {activeJob?.status === "RENDERING_VIDEO" && "3/3. Montando e Concatenação FFmpeg..."}
                      {activeJob?.status === "PENDING" && "Iniciando fila de montagem..."}
                    </p>
                    <p className="text-xs text-slate-400">
                      Montando Full HD 1080p • {activeJob?.progress}% concluído
                    </p>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-white/10">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-500 transition-all duration-500"
                      style={{ width: `${activeJob?.progress || 10}%` }}
                    />
                  </div>
                </div>
              ) : activeJob?.status === "FAILED" ? (
                <div className="p-8 flex flex-col items-center justify-center text-center space-y-3 text-red-400">
                  <AlertTriangle className="h-10 w-10 text-red-400" />
                  <p className="text-sm font-semibold">Falha ao processar vídeo</p>
                  <p className="text-xs text-slate-400 max-w-sm">
                    {activeJob.error_message || "Ocorreu um erro durante a montagem do vídeo."}
                  </p>
                  <button
                    type="button"
                    onClick={handleStartRender}
                    className="px-3.5 py-1.5 rounded-xl bg-red-500/20 hover:bg-red-500/30 text-white text-xs font-semibold cursor-pointer transition-all"
                  >
                    Tentar Novamente
                  </button>
                </div>
              ) : (
                <div className="p-8 flex flex-col items-center justify-center text-center space-y-3 text-slate-500">
                  <Film className="h-12 w-12 text-slate-700" />
                  <div className="space-y-1">
                    <p className="text-sm font-semibold text-slate-400">Nenhum vídeo renderizado ainda</p>
                    <p className="text-xs text-slate-600 max-w-xs">
                      Configure as opções ao lado e clique em &quot;Renderizar Vídeo Final&quot; para iniciar a montagem.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Video Details & Action Footer */}
            {activeJob?.status === "COMPLETED" && (
              <div className="p-5 border-t border-white/10 bg-slate-900/40 flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-3 text-xs text-slate-300 font-mono">
                  <span className="px-2 py-1 rounded-lg bg-black/60 border border-white/10 flex items-center gap-1">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span>{activeJob.duration_seconds}s</span>
                  </span>
                  <span className="px-2 py-1 rounded-lg bg-black/60 border border-white/10 flex items-center gap-1">
                    <Monitor className="h-3 w-3 text-blue-400" />
                    <span>{activeJob.aspect_ratio}</span>
                  </span>
                  <span className="px-2 py-1 rounded-lg bg-black/60 border border-white/10 flex items-center gap-1">
                    <Mic className="h-3 w-3 text-indigo-400" />
                    <span className="truncate max-w-[120px]">{activeJob.voice}</span>
                  </span>
                </div>

                <a
                  href={getRenderVideoStreamUrl(activeJob.id)}
                  download={`framescout-${projectName.toLowerCase().replace(/\s+/g, "-")}.mp4`}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all cursor-pointer"
                >
                  <Download className="h-4 w-4" />
                  <span>Baixar Vídeo (.MP4)</span>
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Studio Configuration Panel (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-3xl bg-slate-900/60 border border-white/10 backdrop-blur space-y-6 shadow-xl">
            <div className="flex items-center gap-2 border-b border-white/10 pb-4">
              <Sparkles className="h-5 w-5 text-indigo-400" />
              <h3 className="font-bold text-white text-base">Configurações de Produção</h3>
            </div>

            {/* Voice Selection */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Mic className="h-3.5 w-3.5 text-blue-400" />
                <span>Voz Neural (Edge-TTS)</span>
              </label>
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
                disabled={Boolean(isRendering)}
                className="w-full bg-slate-950 border border-white/10 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500 transition-all"
              >
                {voices.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Aspect Ratio Format */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="h-3.5 w-3.5 text-indigo-400" />
                <span>Formato de Exibição</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setAspectRatio("16:9")}
                  disabled={Boolean(isRendering)}
                  className={`p-3 rounded-2xl border text-left flex flex-col justify-between gap-2 transition-all cursor-pointer ${
                    aspectRatio === "16:9"
                      ? "bg-blue-600/20 border-blue-500 text-white ring-2 ring-blue-500/20"
                      : "bg-slate-950 border-white/10 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <Monitor className="h-4 w-4 text-blue-400" />
                    <span className="text-[10px] font-mono font-bold">16:9</span>
                  </div>
                  <div>
                    <p className="text-xs font-semibold">Paisagem (YouTube)</p>
                    <p className="text-[10px] text-slate-400">1920x1080 Full HD</p>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setAspectRatio("9:16")}
                  disabled={Boolean(isRendering)}
                  className={`p-3 rounded-2xl border text-left flex flex-col justify-between gap-2 transition-all cursor-pointer ${
                    aspectRatio === "9:16"
                      ? "bg-blue-600/20 border-blue-500 text-white ring-2 ring-blue-500/20"
                      : "bg-slate-950 border-white/10 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <Smartphone className="h-4 w-4 text-indigo-400" />
                    <span className="text-[10px] font-mono font-bold">9:16</span>
                  </div>
                  <div>
                    <p className="text-xs font-semibold">Vertical (Shorts / Reels)</p>
                    <p className="text-[10px] text-slate-400">1080x1920 Full HD</p>
                  </div>
                </button>
              </div>
            </div>

            {/* Toggles */}
            <div className="space-y-3 pt-2 border-t border-white/10">
              <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                <span className="flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4 text-emerald-400" />
                  <span>Slide de Créditos Jurídicos no Final</span>
                </span>
                <input
                  type="checkbox"
                  checked={includeCreditsCard}
                  onChange={(e) => setIncludeCreditsCard(e.target.checked)}
                  disabled={Boolean(isRendering)}
                  className="rounded border-white/20 text-blue-600 focus:ring-blue-500 h-4 w-4"
                />
              </label>
            </div>
          </div>

          {/* Render History List */}
          {jobsHistory.length > 1 && (
            <div className="p-5 rounded-3xl bg-slate-900/40 border border-white/10 space-y-3">
              <h4 className="text-xs font-mono uppercase text-slate-400 tracking-wider">
                Histórico de Versões ({jobsHistory.length})
              </h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {jobsHistory.map((j) => (
                  <button
                    key={j.id}
                    type="button"
                    onClick={() => setActiveJob(j)}
                    className={`w-full p-2.5 rounded-xl text-left text-xs flex items-center justify-between border transition-all cursor-pointer ${
                      activeJob?.id === j.id
                        ? "bg-white/10 border-white/20 text-white"
                        : "bg-slate-950/60 border-white/5 text-slate-400 hover:text-white"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[10px] text-slate-500">
                        {new Date(j.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                      <span className="font-semibold">{j.aspect_ratio}</span>
                    </div>

                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                        j.status === "COMPLETED"
                          ? "bg-emerald-500/10 text-emerald-400"
                          : j.status === "FAILED"
                          ? "bg-red-500/10 text-red-400"
                          : "bg-blue-500/10 text-blue-400"
                      }`}
                    >
                      {j.status}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
