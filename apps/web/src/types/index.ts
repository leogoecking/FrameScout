export type RightsStatus = 
  | "SAFE_REUSE" 
  | "ATTRIBUTION_REQUIRED" 
  | "REVIEW_REQUIRED" 
  | "REFERENCE_ONLY" 
  | "BLOCKED";

export type QueryType =
  | "OFFICIAL"
  | "EVENT"
  | "COMPANY"
  | "PERSON"
  | "LOCATION"
  | "CONCEPT"
  | "BROLL";

export interface Project {
  id: string;
  name: string;
  language: string;
  script_raw?: string | null;
  created_at: string;
  updated_at: string;
  scenes_count?: number;
}

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

export interface SearchQuery {
  id: string;
  scene_id: string;
  query: string;
  query_type: QueryType;
  priority: number;
  created_at: string;
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

export interface SceneSplitRequest {
  first_part_narration: string;
  second_part_narration: string;
  first_part_title?: string | null;
  second_part_title?: string | null;
  first_part_visual_intent?: string | null;
  second_part_visual_intent?: string | null;
}

export interface HealthData {
  status: "ok" | "degraded" | "error";
  service: string;
  environment: string;
  version: string;
  database: "connected" | "disconnected";
  timestamp: string;
}
