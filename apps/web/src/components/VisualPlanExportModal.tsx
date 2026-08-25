"use client";

import { useState } from "react";
import { VisualPlanExport } from "@/types";
import { 
  X, 
  Copy, 
  Check, 
  Download, 
  FileText, 
  Code, 
  Scale, 
  CheckCircle2 
} from "lucide-react";

interface VisualPlanExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan: VisualPlanExport;
}

export function VisualPlanExportModal({
  isOpen,
  onClose,
  plan,
}: VisualPlanExportModalProps) {
  const [activeTab, setActiveTab] = useState<"MARKDOWN" | "JSON" | "CREDITS">("MARKDOWN");
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // Fallback
    }
  };

  const handleDownloadMarkdown = () => {
    const blob = new Blob([plan.markdown_document], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `plano-visual-${plan.project_name.toLowerCase().replace(/\s+/g, "-")}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const creditsContent = plan.consolidated_attributions.length > 0
    ? plan.consolidated_attributions.map((a) => `• ${a}`).join("\n")
    : "Todas as mídias selecionadas são de Domínio Público ou licença aberta comercial livre.";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-950 border border-white/10 rounded-3xl w-full max-w-4xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Plano de Produção Visual</h2>
              <p className="text-xs text-slate-400">
                {plan.project_name} • {plan.total_scenes} cenas • {plan.covered_scenes_count} com mídia
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="h-8 w-8 rounded-full bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tabs Bar */}
        <div className="px-6 py-2.5 border-b border-white/5 flex flex-wrap items-center justify-between gap-3 bg-slate-900/40">
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setActiveTab("MARKDOWN")}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                activeTab === "MARKDOWN"
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <FileText className="h-3.5 w-3.5" />
              <span>Markdown (.md)</span>
            </button>

            <button
              onClick={() => setActiveTab("CREDITS")}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                activeTab === "CREDITS"
                  ? "bg-amber-600 text-white shadow-md shadow-amber-600/20"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <Scale className="h-3.5 w-3.5" />
              <span>Créditos Consolidados ({plan.consolidated_attributions.length})</span>
            </button>

            <button
              onClick={() => setActiveTab("JSON")}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                activeTab === "JSON"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <Code className="h-3.5 w-3.5" />
              <span>JSON Estruturado</span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            {activeTab === "MARKDOWN" && (
              <button
                onClick={handleDownloadMarkdown}
                className="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-medium flex items-center gap-1.5 transition-all"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Baixar .md</span>
              </button>
            )}

            <button
              onClick={() => {
                if (activeTab === "MARKDOWN") handleCopy(plan.markdown_document);
                else if (activeTab === "JSON") handleCopy(JSON.stringify(plan, null, 2));
                else handleCopy(creditsContent);
              }}
              className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-blue-600/20 transition-all"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copied ? "Copiado!" : "Copiar Conteúdo"}</span>
            </button>
          </div>
        </div>

        {/* Content Viewer */}
        <div className="p-6 overflow-y-auto font-mono text-xs text-slate-300 leading-relaxed bg-black/60">
          {activeTab === "MARKDOWN" && (
            <pre className="whitespace-pre-wrap selection:bg-blue-600 selection:text-white">
              {plan.markdown_document}
            </pre>
          )}

          {activeTab === "CREDITS" && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-center gap-2.5">
                <CheckCircle2 className="h-4 w-4 shrink-0" />
                <span>
                  O bloco abaixo reúne todas as citações e licenças obrigatórias compiladas automaticamente das mídias selecionadas.
                </span>
              </div>
              <pre className="p-4 rounded-xl bg-slate-950 border border-white/10 whitespace-pre-wrap selection:bg-amber-600 selection:text-white">
                {creditsContent}
              </pre>
            </div>
          )}

          {activeTab === "JSON" && (
            <pre className="whitespace-pre-wrap selection:bg-indigo-600 selection:text-white">
              {JSON.stringify(plan, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
