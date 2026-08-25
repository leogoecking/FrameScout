import { RightsStatus, MediaType, QueryType } from "./enums";

export interface ProjectCreate {
  name: string;
  language?: string;
  script_raw?: string | null;
}

export interface ProjectUpdate {
  name?: string | null;
  language?: string | null;
  script_raw?: string | null;
}

export interface Project {
  id: string;
  name: string;
  language: string;
  script_raw?: string | null;
  created_at: string;
  updated_at: string;
  scenes_count?: number;
}

export interface Scene {
  id: string;
  project_id: string;
  position: number;
  title?: string | null;
  narration: string;
  visual_intent?: string | null;
  start_estimate?: number | null;
  end_estimate?: number | null;
  created_at: string;
  updated_at: string;
}

export interface SearchQuery {
  id: string;
  scene_id: string;
  query: string;
  query_type: QueryType;
  priority: number;
  created_at: string;
}

export interface MediaCandidate {
  id: string;
  search_query_id?: string | null;
  provider: string;
  external_id: string;
  title?: string | null;
  url: string;
  preview_url: string;
  media_type: MediaType;
  width?: number | null;
  height?: number | null;
  duration?: number | null;
  author?: string | null;
  license?: string | null;
  attribution?: string | null;
  rights_status: RightsStatus;
  fidelity_score?: number | null;
  metadata_json?: Record<string, unknown>;
  created_at: string;
}

export interface HealthStatus {
  status: "ok" | "degraded" | "error";
  service: string;
  environment: string;
  version: string;
  database: "connected" | "disconnected";
  timestamp: string;
}
