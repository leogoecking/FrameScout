import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MediaCandidateCard } from "@/components/MediaCandidateCard";
import { MediaGallery } from "@/components/MediaGallery";
import { MediaCandidate } from "@/types";

const { mockMultiCandidates } = vi.hoisted(() => {
  const mockMultiCandidates: MediaCandidate[] = [
    {
      id: "mc-wiki-1",
      search_query_id: "sq-1",
      provider: "wikimedia",
      external_id: "wikimedia-101",
      title: "Windows Blue Screen of Death (BSOD Error)",
      url: "https://commons.wikimedia.org/wiki/File:Bsodwindows10.png",
      preview_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Bsodwindows10.png/800px-Bsodwindows10.png",
      media_type: "IMAGE",
      width: 1920,
      height: 1080,
      duration: null,
      author: "Wikimedia User",
      license: "CC BY-SA 4.0",
      attribution: "Foto por Wikimedia User sob licença CC BY-SA 4.0 via Wikimedia Commons",
      rights_status: "ATTRIBUTION_REQUIRED",
      fidelity_score: 0.95,
      created_at: "2026-08-25T00:00:00Z",
    },
    {
      id: "mc-wiki-2",
      search_query_id: "sq-1",
      provider: "wikimedia",
      external_id: "wikimedia-102",
      title: "CrowdStrike Logo Vector",
      url: "https://commons.wikimedia.org/wiki/File:CrowdStrike_logo.svg",
      preview_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/CrowdStrike_logo.svg/800px-CrowdStrike_logo.svg.png",
      media_type: "IMAGE",
      width: 1200,
      height: 300,
      duration: null,
      author: "CrowdStrike Holdings",
      license: "Public domain / Trademark",
      attribution: "Logotipo de marca registrada via Wikimedia Commons",
      rights_status: "SAFE_REUSE",
      fidelity_score: 0.95,
      created_at: "2026-08-25T00:00:00Z",
    },
    {
      id: "mc-pex-1",
      search_query_id: "sq-1",
      provider: "pexels",
      external_id: "pexels-325229",
      title: "Servidores em Datacenter",
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
      created_at: "2026-08-25T00:00:00Z",
    },
  ];
  return { mockMultiCandidates };
});

vi.mock("@/lib/api-client", () => ({
  listSceneCandidates: vi.fn().mockResolvedValue(mockMultiCandidates),
  searchSceneMedia: vi.fn().mockResolvedValue(mockMultiCandidates),
}));

describe("Wikimedia Provider & Rights Engine UI", () => {
  it("renders ATTRIBUTION_REQUIRED badge and license name on Wikimedia card", () => {
    render(<MediaCandidateCard candidate={mockMultiCandidates[0]} />);

    expect(screen.getByText("ATRIBUIÇÃO OBRIGATÓRIA")).toBeInTheDocument();
    expect(screen.getByText("CC BY-SA 4.0")).toBeInTheDocument();
    expect(screen.getByText("Wikimedia")).toBeInTheDocument();
    expect(screen.getByText(/Wikimedia User/)).toBeInTheDocument();
  });

  it("filters candidates by provider in MediaGallery (Pexels vs Wikimedia)", async () => {
    render(
      <MediaGallery
        sceneId="scene-1"
        hasQueries={true}
        initialCandidates={mockMultiCandidates}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Wikimedia (2)")).toBeInTheDocument();
      expect(screen.getByText("Pexels (1)")).toBeInTheDocument();
    });

    // Filter to Wikimedia only
    const wikiFilterBtn = screen.getByRole("button", { name: /Wikimedia/i });
    fireEvent.click(wikiFilterBtn);

    expect(
      screen.getByText("Windows Blue Screen of Death (BSOD Error)")
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Servidores em Datacenter")
    ).not.toBeInTheDocument();

    // Filter to Pexels only
    const pexelsFilterBtn = screen.getByRole("button", { name: /Pexels/i });
    fireEvent.click(pexelsFilterBtn);

    expect(
      screen.getByText("Servidores em Datacenter")
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Windows Blue Screen of Death (BSOD Error)")
    ).not.toBeInTheDocument();
  });
});
