import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AIScriptGeneratorModal } from "@/components/AIScriptGeneratorModal";
import { ScriptEditor } from "@/components/ScriptEditor";
import { GenerateScriptResponse } from "@/types";

const { mockGeneratedScript } = vi.hoisted(() => {
  const mockGeneratedScript: GenerateScriptResponse = {
    title: "A Crise da CrowdStrike 2024",
    topic: "O apagão global da CrowdStrike",
    tone: "DOCUMENTARY",
    estimated_duration_seconds: 180,
    word_count: 380,
    script_raw:
      "Cena 01: O Início do Colapso\nEm julho de 2024 uma falha paralisou o mundo.\n\nCena 02: O Resgate\nEngenheiros trabalharam dia e noite.",
    hook: "Em julho de 2024 uma falha paralisou o mundo.",
    call_to_action: "Siga o canal para mais análises.",
  };
  return { mockGeneratedScript };
});

vi.mock("@/lib/api-client", () => ({
  generateScript: vi.fn().mockResolvedValue(mockGeneratedScript),
  generateProjectScript: vi.fn().mockResolvedValue(mockGeneratedScript),
}));

describe("AI Script Generator (Gemini Script Copilot)", () => {
  it("renders AIScriptGeneratorModal with topic input, tone choices and duration selector", () => {
    render(
      <AIScriptGeneratorModal
        isOpen={true}
        onClose={vi.fn()}
        onScriptGenerated={vi.fn()}
      />
    );

    expect(screen.getByText("Criador de Roteiros com IA")).toBeInTheDocument();
    expect(screen.getByText("Gemini Copilot")).toBeInTheDocument();
    expect(screen.getByText("Documental Investigativo")).toBeInTheDocument();
    expect(screen.getByText("Shorts & Reels")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ex: O vazamento do GTA VI/i)).toBeInTheDocument();
  });

  it("triggers script generation and applies script to project", async () => {
    const handleScriptGenerated = vi.fn();
    const handleClose = vi.fn();

    render(
      <AIScriptGeneratorModal
        isOpen={true}
        projectId="proj-123"
        onClose={handleClose}
        onScriptGenerated={handleScriptGenerated}
      />
    );

    const input = screen.getByPlaceholderText(/Ex: O vazamento do GTA VI/i);
    fireEvent.change(input, { target: { value: "O apagão global da CrowdStrike" } });

    const generateBtn = screen.getByRole("button", { name: /Gerar Roteiro com IA/i });
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(screen.getByText("A Crise da CrowdStrike 2024")).toBeInTheDocument();
    });

    const applyBtn = screen.getByRole("button", { name: /Aplicar Roteiro no Projeto/i });
    fireEvent.click(applyBtn);

    expect(handleScriptGenerated).toHaveBeenCalledWith(
      mockGeneratedScript.script_raw,
      mockGeneratedScript
    );
    expect(handleClose).toHaveBeenCalled();
  });

  it("renders '✨ Gerar com IA' button in ScriptEditor and opens modal on click", async () => {
    render(
      <ScriptEditor
        initialScript="Roteiro antigo..."
        projectId="proj-123"
        onSave={vi.fn().mockResolvedValue(undefined)}
      />
    );

    const aiBtn = screen.getByRole("button", { name: /✨ Gerar com IA/i });
    expect(aiBtn).toBeInTheDocument();

    fireEvent.click(aiBtn);

    expect(screen.getByText("Criador de Roteiros com IA")).toBeInTheDocument();
  });
});
