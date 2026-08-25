import { render, screen, waitFor, act } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import HomePage from "@/app/page";

// Mock fetchHealth
vi.mock("@/lib/api-client", () => ({
  fetchHealth: vi.fn().mockResolvedValue({
    status: "ok",
    service: "api",
    environment: "development",
    version: "0.1.0",
    database: "connected",
    timestamp: "2026-08-24T22:00:00Z",
  }),
}));

describe("HomePage", () => {
  it("renders FrameScout title and pipeline description", async () => {
    await act(async () => {
      render(<HomePage />);
    });
    expect(
      screen.getByText("Do roteiro à mídia certa — com procedência e confiança.")
    ).toBeInTheDocument();
    expect(screen.getByText("Status da Infraestrutura (Sprint 0)")).toBeInTheDocument();
  });

  it("displays backend and database connected badges", async () => {
    await act(async () => {
      render(<HomePage />);
    });
    await waitFor(() => {
      expect(screen.getByText(/Conectado \(0.1.0\)/i)).toBeInTheDocument();
      expect(screen.getByText("PostgreSQL 16 • Migrations • UUID Schema")).toBeInTheDocument();
    });
  });

  it("renders pipeline steps from roadmap", async () => {
    await act(async () => {
      render(<HomePage />);
    });
    expect(screen.getByText("1. Roteiro")).toBeInTheDocument();
    expect(screen.getByText("2. Cenas")).toBeInTheDocument();
    expect(screen.getByText("3. Queries")).toBeInTheDocument();
    expect(screen.getByText("4. Providers")).toBeInTheDocument();
    expect(screen.getByText("5. Direitos")).toBeInTheDocument();
    expect(screen.getByText("6. Exportação")).toBeInTheDocument();
  });
});
