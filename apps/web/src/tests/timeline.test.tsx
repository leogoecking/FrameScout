import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { VisualTimeline } from "@/components/VisualTimeline";
import { VisualPlanExportModal } from "@/components/VisualPlanExportModal";
import { VisualPlanExport } from "@/types";

const { mockPlan } = vi.hoisted(() => {
  const mockPlan: VisualPlanExport = {
    project_id: "p-123",
    project_name: "Documentário CrowdStrike",
    language: "pt-BR",
    total_scenes: 2,
    covered_scenes_count: 2,
    total_duration_seconds: 45.0,
    scenes: [
      {
        scene_position: 1,
        scene_title: "Tela Azul Global",
        narration: "A atualização da CrowdStrike travou sistemas em todo o planeta.",
        visual_intent: "Tela azul do Windows e servidores parados",
        start_estimate: 0.0,
        end_estimate: 20.0,
        duration: 20.0,
        selected_asset: {
          id: "sa-1",
          scene_id: "s-1",
          media_candidate_id: "mc-1",
          order_index: 0,
          framing_mode: "PAN_AND_ZOOM",
          notes: "Zoom suave",
          created_at: "2026-08-25T12:00:00Z",
          media_candidate: {
            id: "mc-1",
            provider: "wikimedia",
            external_id: "wiki-bsod",
            title: "Windows BSOD Screenshot",
            url: "https://commons.wikimedia.org/wiki/File:Bsod.png",
            preview_url: "https://upload.wikimedia.org/thumb/bsod.png",
            media_type: "IMAGE",
            width: 1920,
            height: 1080,
            duration: null,
            author: "Wikimedia User",
            license: "CC BY-SA 4.0",
            attribution: "Foto por Wikimedia User sob licença CC BY-SA 4.0",
            rights_status: "ATTRIBUTION_REQUIRED",
            fidelity_score: 0.95,
            created_at: "2026-08-25T12:00:00Z",
          },
        },
      },
      {
        scene_position: 2,
        scene_title: "Aeroportos Paralisados",
        narration: "Painéis de aeroportos exibiam cancelamentos em massa.",
        visual_intent: "Painel de partidas lotado com voos cancelados",
        start_estimate: 20.0,
        end_estimate: 45.0,
        duration: 25.0,
        selected_asset: {
          id: "sa-2",
          scene_id: "s-2",
          media_candidate_id: "mc-2",
          order_index: 0,
          framing_mode: "FILL",
          notes: null,
          created_at: "2026-08-25T12:00:00Z",
          media_candidate: {
            id: "mc-2",
            provider: "pexels",
            external_id: "pexels-airport",
            title: "Airport Departure Board",
            url: "https://pexels.com/photo/123",
            preview_url: "https://images.pexels.com/airport.jpg",
            media_type: "IMAGE",
            width: 1920,
            height: 1080,
            duration: null,
            author: "Pexels Photographer",
            license: "Pexels License",
            attribution: "Foto por Pexels Photographer",
            rights_status: "SAFE_REUSE",
            fidelity_score: 0.9,
            created_at: "2026-08-25T12:00:00Z",
          },
        },
      },
    ],
    consolidated_attributions: [
      "Foto por Wikimedia User sob licença CC BY-SA 4.0",
      "Foto por Pexels Photographer",
    ],
    markdown_document: "# Plano de Produção Visual — Documentário CrowdStrike\n\n## Roteiro...",
  };

  return { mockPlan };
});

vi.mock("@/lib/api-client", () => ({
  exportProjectVisualPlan: vi.fn().mockResolvedValue(mockPlan),
}));

describe("Visual Timeline & Plan Export UI", () => {
  it("renders VisualTimeline with total duration and scene cards", async () => {
    render(<VisualTimeline projectId="p-123" />);

    await waitFor(() => {
      expect(screen.getByText("00:45")).toBeInTheDocument();
      expect(screen.getByText(/2\/2/)).toBeInTheDocument();
      expect(screen.getByText("Tela Azul Global")).toBeInTheDocument();
      expect(screen.getByText("Aeroportos Paralisados")).toBeInTheDocument();
    });

    expect(screen.getByText("PAN_AND_ZOOM")).toBeInTheDocument();
    expect(screen.getByText("FILL")).toBeInTheDocument();
    expect(screen.getByText("ATRIBUIÇÃO OBRIGATÓRIA")).toBeInTheDocument();
  });

  it("renders VisualPlanExportModal and switches tabs to consolidated credits", () => {
    const handleClose = vi.fn();
    render(
      <VisualPlanExportModal
        isOpen={true}
        onClose={handleClose}
        plan={mockPlan}
      />
    );

    expect(screen.getByText("Plano de Produção Visual")).toBeInTheDocument();
    expect(screen.getByText("Markdown (.md)")).toBeInTheDocument();

    // Switch to credits tab
    const creditsTabBtn = screen.getByRole("button", { name: /Créditos Consolidados/i });
    fireEvent.click(creditsTabBtn);

    expect(
      screen.getByText(/O bloco abaixo reúne todas as citações e licenças obrigatórias/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Foto por Wikimedia User sob licença CC BY-SA 4.0/i)
    ).toBeInTheDocument();
  });
});
