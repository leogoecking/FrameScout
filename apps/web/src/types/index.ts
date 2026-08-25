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

export interface HealthData {
  status: "ok" | "degraded" | "error";
  service: string;
  environment: string;
  version: string;
  database: "connected" | "disconnected";
  timestamp: string;
}
