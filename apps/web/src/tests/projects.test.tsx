import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import HomePage from "@/app/page";
import { ScriptEditor } from "@/components/ScriptEditor";

vi.mock("@/lib/api-client", () => ({
  fetchHealth: vi.fn().mockResolvedValue({
    status: "ok",
    service: "api",
    environment: "development",
    version: "0.1.0",
    database: "connected",
    timestamp: "2026-08-24T22:00:00Z",
  }),
  listProjects: vi.fn().mockResolvedValue([
    {
      id: "123e4567-e89b-12d3-a456-426614174000",
      name: "Documentário CrowdStrike",
      language: "pt-BR",
      script_raw: "Em julho de 2024...",
      created_at: "2026-08-24T22:00:00Z",
      updated_at: "2026-08-24T22:00:00Z",
      scenes_count: 0,
    },
  ]),
  createProject: vi.fn().mockResolvedValue({
    id: "987e6543-e89b-12d3-a456-426614174999",
    name: "Projeto Novo",
    language: "pt-BR",
    script_raw: "Roteiro novo",
    created_at: "2026-08-24T22:00:00Z",
    updated_at: "2026-08-24T22:00:00Z",
    scenes_count: 0,
  }),
  deleteProject: vi.fn().mockResolvedValue(undefined),
}));

describe("Projects Management UI", () => {
  it("renders projects list from API", async () => {
    await act(async () => {
      render(<HomePage />);
    });

    await waitFor(() => {
      expect(screen.getByText("Documentário CrowdStrike")).toBeInTheDocument();
      expect(screen.getByText(/Em julho de 2024/i)).toBeInTheDocument();
      expect(screen.getByText("Português")).toBeInTheDocument();
    });
  });

  it("opens Create Project modal on button click", async () => {
    await act(async () => {
      render(<HomePage />);
    });

    const newProjectBtn = screen.getByRole("button", { name: /Novo Projeto/i });
    fireEvent.click(newProjectBtn);

    expect(screen.getByText("Criar Novo Projeto")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ex: Incidente CrowdStrike 2024/i)).toBeInTheDocument();
  });

  it("calculates words, characters and estimates speaking time in ScriptEditor", async () => {
    const onSave = vi.fn().mockResolvedValue(undefined);
    const initialText = "Esta é uma narração de teste para validar o contador de palavras.";

    render(<ScriptEditor initialScript={initialText} onSave={onSave} />);

    expect(screen.getByText(/12\s+palavras/i)).toBeInTheDocument();
    expect(screen.getByText(/65\s+caracteres/i)).toBeInTheDocument();

    const saveButton = screen.getByRole("button", { name: /Salvo/i });
    expect(saveButton).toBeInTheDocument();
  });
});
