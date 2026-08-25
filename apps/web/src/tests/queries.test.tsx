import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { QueryBadge } from "@/components/QueryBadge";
import { SceneQueriesSection } from "@/components/SceneQueriesSection";
import { SearchQuery } from "@/types";

const mockQueries: SearchQuery[] = [
  {
    id: "q-1",
    scene_id: "scene-1",
    query: "CrowdStrike global outage July 2024",
    query_type: "EVENT",
    priority: 1,
    created_at: "2026-08-24T22:00:00Z",
  },
  {
    id: "q-2",
    scene_id: "scene-1",
    query: "CrowdStrike official logo",
    query_type: "OFFICIAL",
    priority: 2,
    created_at: "2026-08-24T22:00:00Z",
  },
  {
    id: "q-3",
    scene_id: "scene-1",
    query: "blue screen of death computer error broll",
    query_type: "BROLL",
    priority: 3,
    created_at: "2026-08-24T22:00:00Z",
  },
];

vi.mock("@/lib/api-client", () => ({
  generateSceneQueries: vi.fn().mockResolvedValue([
    {
      id: "q-new",
      scene_id: "scene-1",
      query: "Take-Two GTA VI leak investigation",
      query_type: "EVENT",
      priority: 1,
      created_at: "2026-08-24T22:00:00Z",
    },
  ]),
  createQuery: vi.fn().mockImplementation((sceneId, data) =>
    Promise.resolve({
      id: "q-created",
      scene_id: sceneId,
      ...data,
      created_at: "2026-08-24T22:00:00Z",
    })
  ),
  updateQuery: vi.fn().mockImplementation((queryId, data) =>
    Promise.resolve({
      id: queryId,
      scene_id: "scene-1",
      query: data.query || "Updated Query",
      query_type: data.query_type || "BROLL",
      priority: data.priority || 1,
      created_at: "2026-08-24T22:00:00Z",
    })
  ),
  deleteQuery: vi.fn().mockResolvedValue(undefined),
}));

describe("Query Generator UI", () => {
  it("renders QueryBadge with type label and query text", () => {
    render(<QueryBadge query={mockQueries[0]} />);

    expect(screen.getByText("Evento")).toBeInTheDocument();
    expect(
      screen.getByText(/CrowdStrike global outage July 2024/)
    ).toBeInTheDocument();
    expect(screen.getByText("P1")).toBeInTheDocument();
  });

  it("renders queries in SceneQueriesSection", () => {
    render(
      <SceneQueriesSection
        sceneId="scene-1"
        initialQueries={mockQueries}
      />
    );

    expect(screen.getByText("Consultas de Busca (3)")).toBeInTheDocument();
    expect(screen.getByText("Oficial")).toBeInTheDocument();
    expect(screen.getByText("B-Roll")).toBeInTheDocument();
  });

  it("generates queries on button click", async () => {
    render(
      <SceneQueriesSection
        sceneId="scene-1"
        initialQueries={[]}
      />
    );

    const generateBtn = screen.getByRole("button", {
      name: /Gerar Queries/i,
    });
    fireEvent.click(generateBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/Take-Two GTA VI leak investigation/)
      ).toBeInTheDocument();
    });
  });
});
