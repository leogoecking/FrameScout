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

export interface SearchQueryCreate {
  query: string;
  query_type?: QueryType;
  priority?: number;
}

export interface SearchQueryUpdate {
  query?: string | null;
  query_type?: QueryType | null;
  priority?: number | null;
}

export interface SearchQuery {
  id: string;
  scene_id: string;
  query: string;
  query_type: QueryType;
  priority: number;
  created_at: string;
  media_candidates?: MediaCandidate[];
}

export interface SceneCreate {
  position?: number | null;
  title?: string | null;
  narration: string;
  visual_intent?: string | null;
  start_estimate?: number | null;
  end_estimate?: number | null;
}

export interface SceneUpdate {
  position?: number | null;
  title?: string | null;
  narration?: string | null;
  visual_intent?: string | null;
  start_estimate?: number | null;
  end_estimate?: number | null;
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
  queries?: SearchQuery[];
}

export interface SceneReorderRequest {
  scene_ids: string[];
}

export interface SceneSplitRequest {
  first_part_narration: string;
  second_part_narration: string;
  first_part_title?: string | null;
  second_part_title?: string | null;
  first_part_visual_intent?: string | null;
  second_part_visual_intent?: string | null;
}

export interface SceneMergeRequest {
  target_scene_id: string;
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
