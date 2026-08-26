"use client";

import { useState } from "react";
import {
  Sparkles,
  X,
  Loader2,
  Clock,
  FileText,
  Check,
  Film,
  Zap,
  BookOpen,
  Tv,
  HelpCircle,
} from "lucide-react";
import { ScriptTone, GenerateScriptResponse } from "@/types";
import { generateScript, generateProjectScript } from "@/lib/api-client";

interface AIScriptGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId?: string;
  onScriptGenerated: (scriptRaw: string, generatedData: GenerateScriptResponse) => void;
}

const QUICK_SUGGESTIONS = [
  "O colapso global da CrowdStrike e o bug no Windows",
  "O vazamento do GTA VI e os bastidores da Rockstar",
  "As descobertas mais profundas do Telescópio James Webb",
  "A guerra dos chips de IA e a dominância da Nvidia",
];

const TONE_OPTIONS: { id: ScriptTone; label: string; desc: string; icon: any }[] = [
  {
    id: "DOCUMENTARY",
    label: "Documental Investigativo",
    desc: "Estilo LOG FATAL / Vox. Fatos, tensão e profundidade.",
    icon: Tv,
  },
  {
    id: "TECH_NEWS",
    label: "Notícias & Tech",
    desc: "Dinâmico, direto e focado em novidades.",
    icon: Zap,
  },
  {
    id: "EXPLAINER",
    label: "Educativo / Didático",
    desc: "Metáforas claras para explicar temas complexos.",
    icon: BookOpen,
  },
  {
    id: "VIRAL_SHORTS",
    label: "Shorts & Reels",
    desc: "Gancho nos primeiros 3s e altíssima retenção.",
    icon: Film,
  },
];

export function AIScriptGeneratorModal({
  isOpen,
  onClose,
  projectId,
  onScriptGenerated,
}: AIScriptGeneratorModalProps) {
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState<ScriptTone>("DOCUMENTARY");
  const [targetDuration, setTargetDuration] = useState("3m");
  const [contextNotes, setContextNotes] = useState("");
  const [autoGenerateScenes, setAutoGenerateScenes] = useState(true);

  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedResult, setGeneratedResult] = useState<GenerateScriptResponse | null>(null);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError("Por favor, digite o tema ou ideia do vídeo.");
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      let result: GenerateScriptResponse;
      if (projectId) {
        result = await generateProjectScript(projectId, {
          topic: topic.trim(),
          tone,
          target_duration: targetDuration,
          context_notes: contextNotes.trim() || undefined,
          auto_generate_scenes: autoGenerateScenes,
        });
      } else {
        result = await generateScript({
          topic: topic.trim(),
          tone,
          target_duration: targetDuration,
          context_notes: contextNotes.trim() || undefined,
        });
      }
      setGeneratedResult(result);
    } catch (err: any) {
      setError(err?.message || "Erro ao gerar roteiro com IA.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleApply = () => {
    if (!generatedResult) return;
    onScriptGenerated(generatedResult.script_raw, generatedResult);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="bg-slate-950 border border-white/15 rounded-3xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-gradient-to-r from-blue-950/40 via-purple-950/30 to-slate-950">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-gradient-to-tr from-blue-600 to-fuchsia-600 text-white shadow-lg shadow-purple-900/30">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                Criador de Roteiros com IA
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/30">
                  Gemini Copilot
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Transforme uma ideia ou notícia em um roteiro estruturado cena a cena.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-all"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs">
          {error && (
            <div className="p-3 bg-red-950/50 border border-red-500/30 rounded-xl text-red-300 text-xs flex items-center gap-2">
              <HelpCircle className="h-4 w-4 shrink-0 text-red-400" />
              <span>{error}</span>
            </div>
          )}

          {!generatedResult ? (
            <>
              {/* Campo de Tema */}
              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold flex items-center justify-between">
                  <span>Tema / Notícia / Ideia Central</span>
                  <span className="text-[10px] text-slate-500">O que você quer contar no vídeo?</span>
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="Ex: O vazamento do GTA VI e o impacto na Rockstar Games"
                  className="w-full px-4 py-3 bg-slate-900/90 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
                />

                {/* Sugestões Rápidas */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  <span className="text-[10px] text-slate-500 font-mono self-center">Sugestões:</span>
                  {QUICK_SUGGESTIONS.map((sug, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => setTopic(sug)}
                      className="px-2 py-0.5 rounded-lg bg-slate-900 border border-white/10 text-[10px] text-slate-400 hover:text-white hover:border-blue-500/40 transition-all truncate max-w-[280px]"
                    >
                      {sug}
                    </button>
                  ))}
                </div>
              </div>

              {/* Seletor de Tom / Estilo */}
              <div className="space-y-2">
                <label className="text-slate-300 font-semibold">Estilo & Tom da Narrativa</label>
                <div className="grid grid-cols-2 gap-2.5">
                  {TONE_OPTIONS.map((opt) => {
                    const Icon = opt.icon;
                    const isSelected = tone === opt.id;
                    return (
                      <div
                        key={opt.id}
                        onClick={() => setTone(opt.id)}
                        className={`p-3 rounded-xl border cursor-pointer transition-all flex items-start gap-2.5 ${
                          isSelected
                            ? "bg-blue-950/40 border-blue-500 text-white shadow-md shadow-blue-950/50"
                            : "bg-slate-900/60 border-white/10 text-slate-400 hover:border-white/20 hover:text-slate-200"
                        }`}
                      >
                        <div
                          className={`p-1.5 rounded-lg ${
                            isSelected ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-400"
                          }`}
                        >
                          <Icon className="h-4 w-4" />
                        </div>
                        <div className="space-y-0.5">
                          <p className="font-semibold text-xs text-white">{opt.label}</p>
                          <p className="text-[10px] text-slate-400 leading-tight">{opt.desc}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Duração Alvo */}
              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold">Duração Estimada</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: "60s", label: "⚡ Shorts (~60s)", desc: "~140 palavras" },
                    { id: "3m", label: "🎬 YouTube (~3 min)", desc: "~380 palavras (Recomendado)" },
                    { id: "5m", label: "📽️ Longo (~5 min)", desc: "~650 palavras" },
                  ].map((dur) => (
                    <button
                      key={dur.id}
                      type="button"
                      onClick={() => setTargetDuration(dur.id)}
                      className={`p-2.5 rounded-xl border text-center transition-all ${
                        targetDuration === dur.id
                          ? "bg-fuchsia-950/40 border-fuchsia-500 text-white"
                          : "bg-slate-900/60 border-white/10 text-slate-400 hover:border-white/20"
                      }`}
                    >
                      <p className="font-bold text-xs">{dur.label}</p>
                      <p className="text-[10px] text-slate-500">{dur.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Instruções Adicionais (Opcional) */}
              <div className="space-y-1.5">
                <label className="text-slate-300 font-semibold flex items-center justify-between">
                  <span>Pontos-chave adicionais (Opcional)</span>
                  <span className="text-[10px] text-slate-500">Detalhes específicos a mencionar</span>
                </label>
                <textarea
                  rows={2}
                  value={contextNotes}
                  onChange={(e) => setContextNotes(e.target.value)}
                  placeholder="Ex: Enfatizar o impacto nas companhias aéreas e no setor bancário..."
                  className="w-full px-3 py-2 bg-slate-900/80 border border-white/10 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Checkbox de auto-geração de cenas caso já esteja em um projeto */}
              {projectId && (
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer pt-1">
                  <input
                    type="checkbox"
                    checked={autoGenerateScenes}
                    onChange={(e) => setAutoGenerateScenes(e.target.checked)}
                    className="rounded border-white/20 bg-slate-900 text-blue-600 focus:ring-0"
                  />
                  <span>Dividir e criar cenas automaticamente após gerar o roteiro</span>
                </label>
              )}
            </>
          ) : (
            /* Prévia do Roteiro Gerado */
            <div className="space-y-4 animate-fade-in">
              <div className="p-4 bg-slate-900/90 border border-white/10 rounded-2xl space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <FileText className="h-4 w-4 text-fuchsia-400" />
                    {generatedResult.title}
                  </h3>
                  <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
                    <span>{generatedResult.word_count} palavras</span>
                    <span>•</span>
                    <span className="text-fuchsia-400 flex items-center gap-1">
                      <Clock className="h-3 w-3" /> ~{Math.round(generatedResult.estimated_duration_seconds / 60)} min
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-400 font-semibold">Roteiro Estruturado em Cenas:</label>
                <textarea
                  rows={10}
                  value={generatedResult.script_raw}
                  onChange={(e) =>
                    setGeneratedResult({
                      ...generatedResult,
                      script_raw: e.target.value,
                    })
                  }
                  className="w-full p-4 bg-slate-950 border border-white/15 rounded-2xl font-mono text-xs text-slate-200 leading-relaxed focus:outline-none focus:border-fuchsia-500"
                />
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-white/10 bg-slate-950/80 flex items-center justify-between">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/5 transition-all"
          >
            Cancelar
          </button>

          {!generatedResult ? (
            <button
              type="button"
              onClick={handleGenerate}
              disabled={isGenerating || !topic.trim()}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-fuchsia-600 hover:from-blue-500 hover:to-fuchsia-500 text-white text-xs font-bold shadow-lg shadow-purple-900/30 flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Roteirizando com Gemini...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Gerar Roteiro com IA</span>
                </>
              )}
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setGeneratedResult(null)}
                className="px-4 py-2 rounded-xl border border-white/10 text-xs font-semibold text-slate-300 hover:bg-white/5 transition-all"
              >
                Gerar Novamente
              </button>
              <button
                type="button"
                onClick={handleApply}
                className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-950/50 flex items-center gap-1.5 transition-all"
              >
                <Check className="h-4 w-4" />
                <span>Aplicar Roteiro no Projeto</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
