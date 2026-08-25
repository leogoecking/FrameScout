import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { SceneList } from "@/components/SceneList";
import { SceneCard } from "@/components/SceneCard";
import { Scene } from "@/types";

const { mockScenes } = vi.hoisted(() => {
  const scenes: Scene[] = [
    {
      id: "scene-1",
      project_id: "proj-1",
      position: 1,
      title: "Cena 01: Pane Global",
      narration: "Uma atualização causou a maior pane global.",
      visual_intent: "B-roll de tela azul da morte",
      start_estimate: 0.0,
      end_estimate: 5.5,
      created_at: "2026-08-24T22:00:00Z",
      updated_at: "2026-08-24T22:00:00Z",
    },
    {
      id: "scene-2",
      project_id: "proj-1",
      position: 2,
      title: "Cena 02: Aeroportos",
      narration: "Voos cancelados e passageiros no saguão.",
      visual_intent: "B-roll de aeroporto lotado",
      start_estimate: 5.5,
      end_estimate: 11.0,
      created_at: "2026-08-24T22:00:00Z",
      updated_at: "2026-08-24T22:00:00Z",
    },
  ];
  return { mockScenes: scenes };
});

vi.mock("@/lib/api-client", () => ({
  generateScenes: vi.fn().mockResolvedValue(mockScenes),
  createScene: vi.fn().mockResolvedValue({
    id: "scene-3",
    project_id: "proj-1",
    position: 3,
    title: "Cena 03",
    narration: "Nova narração",
    visual_intent: "Novo visual",
    start_estimate: 11.0,
    end_estimate: 15.0,
    created_at: "2026-08-24T22:00:00Z",
    updated_at: "2026-08-24T22:00:00Z",
  }),
  updateScene: vi.fn().mockImplementation((id, data) =>
    Promise.resolve({ ...mockScenes[0], ...data })
  ),
  deleteScene: vi.fn().mockResolvedValue(undefined),
  reorderScenes: vi.fn().mockResolvedValue(mockScenes),
  splitScene: vi.fn().mockResolvedValue([mockScenes[0], mockScenes[1]]),
  mergeScenes: vi.fn().mockResolvedValue(mockScenes[0]),
}));

describe("Scene Engine UI", () => {
  it("renders list of scenes with positions, titles and visual intents", () => {
    render(
      <SceneList
        projectId="proj-1"
        hasScript={true}
        initialScenes={mockScenes}
      />
    );

    expect(screen.getByText("CENA 01")).toBeInTheDocument();
    expect(screen.getByText("CENA 02")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Cena 01: Pane Global")).toBeInTheDocument();
    expect(screen.getByDisplayValue("B-roll de tela azul da morte")).toBeInTheDocument();
    expect(screen.getByText("2 Cenas")).toBeInTheDocument();
  });

  it("triggers automatic scene generation when button clicked", async () => {
    render(
      <SceneList
        projectId="proj-1"
        hasScript={true}
        initialScenes={[]}
      />
    );

    const generateBtn = screen.getByRole("button", {
      name: /Gerar Cenas Automaticamente/i,
    });
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(screen.getByText("CENA 01")).toBeInTheDocument();
    });
  });

  it("handles inline update on SceneCard blur", async () => {
    const onUpdate = vi.fn().mockResolvedValue(undefined);
    render(
      <SceneCard
        scene={mockScenes[0]}
        isFirst={true}
        isLast={false}
        onUpdate={onUpdate}
        onDelete={vi.fn().mockResolvedValue(undefined)}
        onMoveUp={vi.fn().mockResolvedValue(undefined)}
        onMoveDown={vi.fn().mockResolvedValue(undefined)}
        onOpenSplit={vi.fn()}
        onMergeWithNext={vi.fn().mockResolvedValue(undefined)}
      />
    );

    const titleInput = screen.getByDisplayValue("Cena 01: Pane Global");
    fireEvent.change(titleInput, { target: { value: "Cena 01: Título Alterado" } });
    fireEvent.blur(titleInput);

    await waitFor(() => {
      expect(onUpdate).toHaveBeenCalledWith("scene-1", expect.objectContaining({
        title: "Cena 01: Título Alterado",
      }));
    });
  });
});
