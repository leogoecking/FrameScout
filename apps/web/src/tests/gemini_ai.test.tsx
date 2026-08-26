import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MediaCandidateCard } from "@/components/MediaCandidateCard";
import { MediaGallery } from "@/components/MediaGallery";
import { MediaCandidate } from "@/types";

const { mockAICandidates } = vi.hoisted(() => {
  const mockAICandidates: MediaCandidate[] = [
    {
      id: "ai-cand-1",
      search_query_id: "sq-1",
      provider: "gemini",
      external_id: "gemini_12345",
      title: "Imagem IA: Computação Quântica Holográfica",
      url: "/media/gemini_12345_0.jpg",
      preview_url: "/media/gemini_12345_0.jpg",
      media_type: "IMAGE",
      width: 1920,
      height: 1080,
      duration: null,
      author: "Google Imagen 3 (Gemini)",
      license: "AI Generated (Open Commercial Use)",
      attribution: "Gerado por IA (Google Imagen 3 / Gemini)",
      rights_status: "SAFE_REUSE",
      fidelity_score: 0.96,
      created_at: "2026-08-25T23:00:00Z",
      metadata_json: {
        ai_generated: true,
        model: "imagen-3.0-generate-002",
      },
    },
  ];
  return { mockAICandidates };
});

vi.mock("@/lib/api-client", () => ({
  listSceneCandidates: vi.fn().mockResolvedValue(mockAICandidates),
  listSceneSelectedAssets: vi.fn().mockResolvedValue([]),
  searchSceneMedia: vi.fn().mockResolvedValue(mockAICandidates),
  rerankSceneCandidates: vi.fn().mockResolvedValue(mockAICandidates),
  generateSceneAIImage: vi.fn().mockResolvedValue(mockAICandidates),
}));

describe("AI Media Generation UI (Google Imagen 3 / Gemini)", () => {
  it("renders MediaCandidateCard with Gemini IA badge and open commercial use license", () => {
    render(<MediaCandidateCard candidate={mockAICandidates[0]} />);

    expect(screen.getByText("✨ Gemini IA")).toBeInTheDocument();
    expect(screen.getByText("SAFE_REUSE")).toBeInTheDocument();
    expect(screen.getByText(/Google Imagen 3/i)).toBeInTheDocument();
  });

  it("renders 'Gerar com IA' button in MediaGallery and triggers generation", async () => {
    const { generateSceneAIImage } = await import("@/lib/api-client");

    render(
      <MediaGallery
        sceneId="scene-1"
        hasQueries={true}
        initialCandidates={mockAICandidates}
      />
    );

    const aiButton = screen.getByRole("button", { name: /Gerar com IA/i });
    expect(aiButton).toBeInTheDocument();

    fireEvent.click(aiButton);

    await waitFor(() => {
      expect(generateSceneAIImage).toHaveBeenCalledWith("scene-1", {
        aspect_ratio: "16:9",
        count: 2,
      });
    });
  });

  it("filters candidates by Gemini IA in MediaGallery", () => {
    render(
      <MediaGallery
        sceneId="scene-1"
        hasQueries={true}
        initialCandidates={mockAICandidates}
      />
    );

    const geminiFilter = screen.getByRole("button", { name: /IA Gemini/i });
    expect(geminiFilter).toBeInTheDocument();
    fireEvent.click(geminiFilter);
    expect(screen.getByText("Imagem IA: Computação Quântica Holográfica")).toBeInTheDocument();
  });
});
