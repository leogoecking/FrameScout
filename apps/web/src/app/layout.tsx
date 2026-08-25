import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FrameScout — Do Roteiro à Mídia Certa",
  description:
    "Transforme roteiros em cenas e encontre imagens, vídeos, B-rolls e referências visuais com procedência e direitos de uso rigorosos.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="antialiased selection:bg-blue-600 selection:text-white">
        <header className="border-b border-white/10 bg-slate-950/70 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-500 via-indigo-500 to-emerald-500 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/20">
                FS
              </div>
              <div>
                <span className="font-semibold text-lg tracking-tight text-white">FrameScout</span>
                <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono">
                  Sprint 7
                </span>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-slate-400">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="hover:text-white transition-colors flex items-center gap-1.5"
              >
                <span>API Docs</span>
                <span className="text-xs">↗</span>
              </a>
              <span className="text-slate-700">•</span>
              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer"
                className="hover:text-white transition-colors"
              >
                GitHub
              </a>
            </div>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
