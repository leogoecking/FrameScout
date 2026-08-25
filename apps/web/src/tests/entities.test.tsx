import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { SceneQueriesSection } from "@/components/SceneQueriesSection";

vi.mock("@/lib/api-client", () => ({
  generateSceneQueries: vi.fn().mockResolvedValue([]),
  createQuery: vi.fn().mockImplementation((sceneId, data) =>
    Promise.resolve({
      id: "q-created",
      scene_id: sceneId,
      ...data,
      created_at: "2026-08-25T20:00:00Z",
    })
  ),
  updateQuery: vi.fn(),
  deleteQuery: vi.fn(),
  extractSceneEntities: vi.fn().mockResolvedValue({
    scene_id: "scene-1",
    scene_position: 1,
    entities: [
      {
        text: "CrowdStrike",
        category: "ORGANIZATION",
        confidence: 0.95,
        context: "a empresa CrowdStrike...",
      },
      {
        text: "Falcon Sensor",
        category: "PRODUCT",
        confidence: 0.95,
        context: "atualização do Falcon Sensor...",
      },
      {
        text: "Sam Altman",
        category: "PERSON",
        confidence: 0.98,
        context: "depoimento de Sam Altman...",
      },
      {
        text: "Julho de 2024",
        category: "DATE_TIME",
        confidence: 0.95,
        context: "em Julho de 2024...",
      },
    ],
    suggested_queries: [],
  }),
}));

describe("Entity Extraction UI (Sprint 13)", () => {
  it("renders Extrair Entidades button in SceneQueriesSection", () => {
    render(
      <SceneQueriesSection
        sceneId="scene-1"
        initialQueries={[]}
      />
    );

    expect(
      screen.getByRole("button", { name: /Extrair Entidades/i })
    ).toBeInTheDocument();
  });

  it("extracts and renders categorized entity chips on button click", async () => {
    const onQueriesUpdated = vi.fn();
    render(
      <SceneQueriesSection
        sceneId="scene-1"
        initialQueries={[]}
        onQueriesUpdated={onQueriesUpdated}
      />
    );

    const extractBtn = screen.getByRole("button", { name: /Extrair Entidades/i });
    fireEvent.click(extractBtn);

    await waitFor(() => {
      expect(screen.getByText("Entidades Detectadas (4):")).toBeInTheDocument();
      expect(screen.getByText("CrowdStrike")).toBeInTheDocument();
      expect(screen.getByText("Falcon Sensor")).toBeInTheDocument();
      expect(screen.getByText("Sam Altman")).toBeInTheDocument();
      expect(screen.getByText("Julho de 2024")).toBeInTheDocument();
      expect(screen.getByText("[Org]")).toBeInTheDocument();
      expect(screen.getByText("[Produto]")).toBeInTheDocument();
      expect(screen.getByText("[Pessoa]")).toBeInTheDocument();
      expect(screen.getByText("[Data]")).toBeInTheDocument();
    });
  });

  it("adds entity as a new query on + button click", async () => {
    const onQueriesUpdated = vi.fn();
    render(
      <SceneQueriesSection
        sceneId="scene-1"
        initialQueries={[]}
        onQueriesUpdated={onQueriesUpdated}
      />
    );

    const extractBtn = screen.getByRole("button", { name: /Extrair Entidades/i });
    fireEvent.click(extractBtn);

    await waitFor(() => {
      expect(screen.getByText("CrowdStrike")).toBeInTheDocument();
    });

    const addQueryBtns = screen.getAllByTitle(/Criar query de busca para/i);
    expect(addQueryBtns.length).toBe(4);

    fireEvent.click(addQueryBtns[0]);

    await waitFor(() => {
      expect(onQueriesUpdated).toHaveBeenCalled();
    });
  });
});
