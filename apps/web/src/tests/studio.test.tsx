import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { VideoStudioPlayer } from "@/components/VideoStudioPlayer";
import * as apiClient from "@/lib/api-client";
import { RenderJob, VoiceOption } from "@/types";

vi.mock("@/lib/api-client", () => ({
  listAvailableVoices: vi.fn(),
  listProjectRenderJobs: vi.fn(),
  triggerRenderJob: vi.fn(),
  getRenderJob: vi.fn(),
  getRenderVideoStreamUrl: vi.fn((id: string) => `http://localhost:8000/api/v1/render-jobs/${id}/stream`),
}));

const mockVoices: VoiceOption[] = [
  { id: "pt-BR-AntonioNeural", name: "Antonio (Masculino, Natural)" },
  { id: "pt-BR-FranciscaNeural", name: "Francisca (Feminino, Expressivo)" },
];

const mockCompletedJob: RenderJob = {
  id: "job-1234",
  project_id: "proj-1",
  status: "COMPLETED",
  progress: 100,
  aspect_ratio: "16:9",
  voice: "pt-BR-AntonioNeural",
  include_subtitles: true,
  include_credits_card: true,
  video_url: "/api/v1/render-jobs/job-1234/stream",
  duration_seconds: 12.5,
  error_message: null,
  created_at: "2026-08-25T12:00:00Z",
  updated_at: "2026-08-25T12:00:10Z",
};

describe("VideoStudioPlayer UI (Sprint 7)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders voice selector, aspect ratio format options and render trigger button", async () => {
    vi.mocked(apiClient.listAvailableVoices).mockResolvedValue(mockVoices);
    vi.mocked(apiClient.listProjectRenderJobs).mockResolvedValue([]);

    render(
      <VideoStudioPlayer
        projectId="proj-1"
        projectName="Documentário CrowdStrike"
        totalScenes={3}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Motor de Montagem e Renderização de Vídeo/i)).toBeInTheDocument();
    });

    expect(screen.getByText("Antonio (Masculino, Natural)")).toBeInTheDocument();
    expect(screen.getByText(/Paisagem \(YouTube\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Vertical \(Shorts \/ Reels\)/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Renderizar Vídeo Final/i })).toBeInTheDocument();
  });

  it("renders completed video player when job is COMPLETED", async () => {
    vi.mocked(apiClient.listAvailableVoices).mockResolvedValue(mockVoices);
    vi.mocked(apiClient.listProjectRenderJobs).mockResolvedValue([mockCompletedJob]);

    render(
      <VideoStudioPlayer
        projectId="proj-1"
        projectName="Documentário CrowdStrike"
        totalScenes={3}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(/Pronto \(12.5s\)/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Baixar Vídeo \(\.MP4\)/i)).toBeInTheDocument();
  });

  it("triggers render job when clicking render button", async () => {
    vi.mocked(apiClient.listAvailableVoices).mockResolvedValue(mockVoices);
    vi.mocked(apiClient.listProjectRenderJobs).mockResolvedValue([]);
    vi.mocked(apiClient.triggerRenderJob).mockResolvedValue({
      ...mockCompletedJob,
      status: "SYNTHESIZING_AUDIO",
      progress: 15,
    });

    render(
      <VideoStudioPlayer
        projectId="proj-1"
        projectName="Documentário CrowdStrike"
        totalScenes={3}
      />
    );

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Renderizar Vídeo Final/i })).toBeInTheDocument();
    });

    const renderBtn = screen.getByRole("button", { name: /Renderizar Vídeo Final/i });
    fireEvent.click(renderBtn);

    await waitFor(() => {
      expect(apiClient.triggerRenderJob).toHaveBeenCalledWith("proj-1", {
        aspect_ratio: "16:9",
        voice: "pt-BR-AntonioNeural",
        include_subtitles: true,
        include_credits_card: true,
      });
    });
  });
});
