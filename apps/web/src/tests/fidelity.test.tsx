import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MediaCandidateCard } from "@/components/MediaCandidateCard";
import { MediaGallery } from "@/components/MediaGallery";
import { MediaCandidate } from "@/types";

const mockCandidateHighFidelity: MediaCandidate = {
  id: "cand-high",
  search_query_id: "query-1",
  provider: "wikimedia",
  external_id: "wiki-bsod",
  title: "Windows Blue Screen of Death BSOD CrowdStrike",
  url: "https://commons.wikimedia.org/wiki/File:Bsod.png",
  preview_url: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Bsod.png/960px-Bsod.png",
  media_type: "IMAGE",
  width: 1920,
  height: 1080,
  duration: null,
  author: "Wikimedia Contributor",
  license: "CC BY-SA 4.0",
  attribution: "Atribuição Wikimedia",
  rights_status: "ATTRIBUTION_REQUIRED",
  fidelity_score: 0.95,
  metadata_json: {
    fidelity_breakdown: {
      semantic: 38.0,
      entities: 24.5,
      authority: 14.2,
      temporal: 10.0,
      quality: 10.0,
      total: 95.0,
    },
  },
  created_at: "2026-08-25T10:00:00Z",
};

const mockCandidateBroll: MediaCandidate = {
  id: "cand-broll",
  search_query_id: "query-1",
  provider: "pexels",
  external_id: "pexels-office",
  title: "Office computer desk working",
  url: "https://pexels.com/photo/123",
  preview_url: "https://images.pexels.com/photos/123/desk.jpg",
  media_type: "IMAGE",
  width: 1920,
  height: 1080,
  duration: null,
  author: "Pexels Photographer",
  license: "Pexels License",
  attribution: "Pexels Foto",
  rights_status: "SAFE_REUSE",
  fidelity_score: 0.65,
  metadata_json: {
    fidelity_breakdown: {
      semantic: 22.0,
      entities: 10.0,
      authority: 12.0,
      temporal: 6.0,
      quality: 10.0,
      total: 65.0,
    },
  },
  created_at: "2026-08-25T10:00:00Z",
};

describe("Semantic Ranking & Fidelity Score UI (Sprint 11/12)", () => {
  it("renders fidelity score badge on candidate card and toggles breakdown on click", () => {
    render(<MediaCandidateCard candidate={mockCandidateHighFidelity} />);

    // Deve exibir 95% Fidelidade
    const badge = screen.getByText("95% Fidelidade");
    expect(badge).toBeInTheDocument();

    // Clicar no badge para abrir o popover de detalhamento
    fireEvent.click(badge);

    expect(screen.getByText("Avaliação de Fidelidade")).toBeInTheDocument();
    expect(screen.getByText("95/100")).toBeInTheDocument();
    expect(screen.getByText(/Semântica:/i)).toBeInTheDocument();
    expect(screen.getByText(/Entidades:/i)).toBeInTheDocument();
  });

  it("filters candidates by fidelity score in MediaGallery (All vs High vs BRoll)", () => {
    render(
      <MediaGallery
        sceneId="scene-test-fid"
        hasQueries={true}
        initialCandidates={[mockCandidateHighFidelity, mockCandidateBroll]}
      />
    );

    expect(screen.getByText("Windows Blue Screen of Death BSOD CrowdStrike")).toBeInTheDocument();
    expect(screen.getByText("Office computer desk working")).toBeInTheDocument();

    // Filtrar apenas Alta Fidelidade (≥80%)
    const highFilterBtn = screen.getByText("≥80% Alta");
    fireEvent.click(highFilterBtn);

    expect(screen.getByText("Windows Blue Screen of Death BSOD CrowdStrike")).toBeInTheDocument();
    expect(screen.queryByText("Office computer desk working")).not.toBeInTheDocument();

    // Filtrar apenas B-Roll (50-79%)
    const brollFilterBtn = screen.getByText("50-79% B-Roll");
    fireEvent.click(brollFilterBtn);

    expect(screen.queryByText("Windows Blue Screen of Death BSOD CrowdStrike")).not.toBeInTheDocument();
    expect(screen.getByText("Office computer desk working")).toBeInTheDocument();
  });
});
