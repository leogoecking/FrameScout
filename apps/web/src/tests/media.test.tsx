import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MediaCandidateCard } from "@/components/MediaCandidateCard";
import { MediaGallery } from "@/components/MediaGallery";
import { MediaCandidate } from "@/types";

const { mockCandidates } = vi.hoisted(() => {
  const mockCandidates: MediaCandidate[] = [
    {
      id: "mc-1",
      search_query_id: "sq-1",
      provider: "pexels",
      external_id: "pexels-325229",
      title: "Servidores em Datacenter com luzes azuis",
      url: "https://www.pexels.com/photo/325229/",
      preview_url: "https://images.pexels.com/photos/325229/pexels-photo-325229.jpeg",
      media_type: "IMAGE",
      width: 1920,
      height: 1080,
      duration: null,
      author: "Manuel Geissinger",
      license: "Pexels License",
      attribution: "Foto por Manuel Geissinger no Pexels",
      rights_status: "SAFE_REUSE",
      fidelity_score: 0.9,
      created_at: "2026-08-24T23:00:00Z",
    },
    {
      id: "mc-2",
      search_query_id: "sq-1",
      provider: "pexels",
      external_id: "pexels-3129957",
      title: "Linhas de Código e Terminal",
      url: "https://www.pexels.com/video/3129957/",
      preview_url: "https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg",
      media_type: "VIDEO",
      width: 3840,
      height: 2160,
      duration: 14.5,
      author: "Pressmaster",
      license: "Pexels License",
      attribution: "Vídeo por Pressmaster no Pexels",
      rights_status: "SAFE_REUSE",
      fidelity_score: 0.92,
      created_at: "2026-08-24T23:00:00Z",
    },
  ];
  return { mockCandidates };
});

vi.mock("@/lib/api-client", () => ({
  listSceneCandidates: vi.fn().mockResolvedValue(mockCandidates),
  searchSceneMedia: vi.fn().mockResolvedValue(mockCandidates),
}));

describe("Media Provider UI (Pexels)", () => {
  it("renders MediaCandidateCard with SAFE_REUSE badge, resolution and author", () => {
    render(<MediaCandidateCard candidate={mockCandidates[0]} />);

    expect(screen.getByText("SAFE_REUSE")).toBeInTheDocument();
    expect(screen.getByText("1920x1080")).toBeInTheDocument();
    expect(screen.getByText(/Manuel Geissinger/)).toBeInTheDocument();
    expect(screen.getByText("Foto")).toBeInTheDocument();
  });

  it("renders video card with duration and video tag", () => {
    render(<MediaCandidateCard candidate={mockCandidates[1]} />);

    expect(screen.getByText("Vídeo")).toBeInTheDocument();
    expect(screen.getByText(/0:14/)).toBeInTheDocument();
    expect(screen.getByText("3840x2160")).toBeInTheDocument();
  });

  it("renders MediaGallery and filters by type", async () => {
    render(
      <MediaGallery
        sceneId="scene-1"
        hasQueries={true}
        initialCandidates={mockCandidates}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Todos (2)")).toBeInTheDocument();
    });

    // Filter to videos only
    const videoFilterBtn = screen.getByRole("button", { name: /Vídeos/i });
    fireEvent.click(videoFilterBtn);

    expect(
      screen.getByText("Linhas de Código e Terminal")
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Servidores em Datacenter com luzes azuis")
    ).not.toBeInTheDocument();
  });

  it("triggers search on button click in MediaGallery", async () => {
    render(
      <MediaGallery
        sceneId="scene-1"
        hasQueries={true}
        initialCandidates={[]}
      />
    );

    const searchBtn = screen.getByRole("button", {
      name: /Buscar Mídia no Pexels|Atualizar Busca Pexels/i,
    });
    fireEvent.click(searchBtn);

    await waitFor(() => {
      expect(
        screen.getByText("Servidores em Datacenter com luzes azuis")
      ).toBeInTheDocument();
    });
  });
});
