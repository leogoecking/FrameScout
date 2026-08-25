"use client";

import { useState, useEffect } from "react";
import { X, Search, Loader2 } from "lucide-react";
import { QueryType, SearchQuery, SearchQueryCreate, SearchQueryUpdate } from "@/types";

interface QueryEditorModalProps {
  queryToEdit?: SearchQuery | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: SearchQueryCreate | SearchQueryUpdate) => Promise<void>;
}

export function QueryEditorModal({
  queryToEdit,
  isOpen,
  onClose,
  onSave,
}: QueryEditorModalProps) {
  const [term, setTerm] = useState("");
  const [type, setType] = useState<QueryType>("BROLL");
  const [priority, setPriority] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      if (queryToEdit) {
        setTerm(queryToEdit.query);
        setType(queryToEdit.query_type);
        setPriority(queryToEdit.priority);
      } else {
        setTerm("");
        setType("BROLL");
        setPriority(1);
      }
      setError(null);
    }
  }, [queryToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!term.trim()) {
      setError("O termo de busca não pode estar vazio.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await onSave({
        query: term.trim(),
        query_type: type,
        priority: priority,
      });
      onClose();
    } catch (err: any) {
      setError(err?.message || "Erro ao salvar query de busca.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-white/10 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center">
              <Search className="h-4 w-4" />
            </div>
            <h3 className="text-lg font-semibold text-white">
              {queryToEdit ? "Editar Query de Busca" : "Nova Query de Busca"}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/5 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
              {error}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
              Termo de Busca / Prompt
            </label>
            <input
              type="text"
              required
              value={term}
              onChange={(e) => setTerm(e.target.value)}
              placeholder="Ex: CrowdStrike Falcon Sensor BSOD outage"
              className="w-full bg-slate-950/60 border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500 transition-all placeholder:text-slate-600"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
                Tipo de Busca
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as QueryType)}
                className="w-full bg-slate-950/60 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 transition-all"
              >
                <option value="EVENT">Evento / Fato Direto</option>
                <option value="OFFICIAL">Fonte Oficial / Logotipo</option>
                <option value="BROLL">B-Roll / Atmosférico</option>
                <option value="COMPANY">Empresa / Institucional</option>
                <option value="PERSON">Pessoa / Executivo</option>
                <option value="LOCATION">Local / Cidade</option>
                <option value="CONCEPT">Conceito / Metáfora</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
                Prioridade (1 = Alta)
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(Number(e.target.value))}
                className="w-full bg-slate-950/60 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 transition-all"
              >
                <option value={1}>1 - Alta (Principal)</option>
                <option value={2}>2 - Média (Secundária)</option>
                <option value={3}>3 - Baixa (Fallback)</option>
                <option value={4}>4 - Opcional</option>
                <option value={5}>5 - Referência</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium flex items-center gap-2 shadow-lg shadow-blue-600/20 disabled:opacity-50 transition-all"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              {queryToEdit ? "Salvar Alterações" : "Criar Busca"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
