"use client";

import { useState, useEffect } from "react";
import { Save, Check, Loader2, FileCode, AlertCircle } from "lucide-react";

interface ScriptEditorProps {
  initialScript: string;
  onSave: (script: string) => Promise<void>;
}

export function ScriptEditor({ initialScript, onSave }: ScriptEditorProps) {
  const [script, setScript] = useState(initialScript || "");
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setScript(initialScript || "");
    setIsSaved(true);
  }, [initialScript]);

  // Track word & character count
  const charCount = script.length;
  const wordCount = script.trim() ? script.trim().split(/\s+/).length : 0;
  const estMinutes = (wordCount / 130).toFixed(1); // Média de 130 palavras por minuto falado

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    try {
      await onSave(script);
      setIsSaved(true);
    } catch (err: any) {
      setError(err?.message || "Erro ao salvar roteiro.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      e.preventDefault();
      handleSave();
    }
  };

  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl overflow-hidden shadow-xl flex flex-col">
      {/* Editor Toolbar */}
      <div className="px-6 py-3.5 border-b border-white/10 bg-slate-950/60 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileCode className="h-4 w-4 text-blue-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Editor de Roteiro
          </span>
          <span className="text-xs text-slate-500 font-mono hidden sm:inline">
            (Pressione Ctrl+S para salvar)
          </span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-slate-400 font-mono pr-2 border-r border-white/10">
            <span>{wordCount} palavras</span>
            <span>•</span>
            <span>{charCount} caracteres</span>
            <span>•</span>
            <span className="text-blue-400">~{estMinutes} min narração</span>
          </div>

          <button
            onClick={handleSave}
            disabled={isSaving || isSaved}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all ${
              isSaved
                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 cursor-default"
                : "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20"
            }`}
          >
            {isSaving ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Salvando...</span>
              </>
            ) : isSaved ? (
              <>
                <Check className="h-3.5 w-3.5" />
                <span>Salvo</span>
              </>
            ) : (
              <>
                <Save className="h-3.5 w-3.5" />
                <span>Salvar Roteiro</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="px-6 py-2 bg-red-500/10 border-b border-red-500/20 text-red-400 text-xs flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Editor Body */}
      <div className="p-6 flex-1 flex flex-col">
        <textarea
          value={script}
          onChange={(e) => {
            setScript(e.target.value);
            setIsSaved(false);
          }}
          onKeyDown={handleKeyDown}
          placeholder="Cole ou digite aqui o roteiro completo do seu vídeo. Exemplo:

Cena 1: Em julho de 2024, uma atualização falha da CrowdStrike causou uma pane global em milhões de computadores Windows.

Cena 2: Voos foram cancelados, hospitais paralisaram atendimentos e caixas eletrônicos exibiram a famosa tela azul da morte..."
          className="w-full h-96 bg-transparent text-slate-100 placeholder:text-slate-600 text-sm leading-relaxed focus:outline-none resize-y font-sans selection:bg-blue-600 selection:text-white"
        />
      </div>
    </div>
  );
}
