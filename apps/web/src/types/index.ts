export type RightsStatus = 
  | "SAFE_REUSE" 
  | "ATTRIBUTION_REQUIRED" 
  | "REVIEW_REQUIRED" 
  | "REFERENCE_ONLY" 
  | "BLOCKED";

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
