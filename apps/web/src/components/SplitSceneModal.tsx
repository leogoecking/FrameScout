"use client";

import { useState, useEffect } from "react";
import { X, Scissors, Loader2 } from "lucide-react";
import { Scene, SceneSplitRequest } from "@/types";

interface SplitSceneModalProps {
  scene: Scene | null;
  isOpen: boolean;
  onClose: () => void;
  onSplit: (sceneId: string, data: SceneSplitRequest) => Promise<void>;
}

export function SplitSceneModal({ scene, isOpen, onClose, onSplit }: SplitSceneModalProps) {
  const [part1, setPart1] = useState("");
  const [part2, setPart2] = useState("");
  const [title1, setTitle1] = useState("");
  const [title2, setTitle2] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (scene && isOpen) {
      const words = scene.narration.trim().split(/\s+/);
      const mid = Math.max(1, Math.ceil(words.length / 2));
      setPart1(words.slice(0, mid).join(" "));
      setPart2(words.slice(mid).join(" "));
      setTitle1(`${scene.title || `Cena ${scene.position}`} (Parte 1)`);
      setTitle2(`${scene.title || `Cena ${scene.position}`} (Parte 2)`);
      setError(null);
    }
  }, [scene, isOpen]);

  if (!isOpen || !scene) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!part1.trim() || !part2.trim()) {
      setError("Ambas as partes da cena devem possuir texto de narração.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await onSplit(scene.id, {
        first_part_narration: part1.trim(),
        second_part_narration: part2.trim(),
        first_part_title: title1.trim() || undefined,
        second_part_title: title2.trim() || undefined,
      });
      onClose();
    } catch (err: any) {
      setError(err?.message || "Erro ao dividir cena.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-white/10 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center">
              <Scissors className="h-4 w-4" />
            </div>
            <h3 className="text-lg font-semibold text-white">Dividir Cena {scene.position}</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-white/5 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Part 1 */}
            <div className="space-y-2 bg-slate-950/60 p-4 rounded-xl border border-white/5">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-blue-400 uppercase tracking-wider">
                  Título - 1ª Parte
                </label>
                <input
                  type="text"
                  value={title1}
                  onChange={(e) => setTitle1(e.target.value)}
                  className="w-full bg-slate-900 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Narração - 1ª Parte
                </label>
                <textarea
                  rows={6}
                  value={part1}
                  onChange={(e) => setPart1(e.target.value)}
                  className="w-full bg-slate-900 border border-white/10 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-blue-500 resize-none leading-relaxed"
                />
              </div>
            </div>

            {/* Part 2 */}
            <div className="space-y-2 bg-slate-950/60 p-4 rounded-xl border border-white/5">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                  Título - 2ª Parte
                </label>
                <input
                  type="text"
                  value={title2}
                  onChange={(e) => setTitle2(e.target.value)}
                  className="w-full bg-slate-900 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Narração - 2ª Parte
                </label>
                <textarea
                  rows={6}
                  value={part2}
                  onChange={(e) => setPart2(e.target.value)}
                  className="w-full bg-slate-900 border border-white/10 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 resize-none leading-relaxed"
                />
              </div>
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
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Scissors className="h-4 w-4" />}
              Confirmar Divisão
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
