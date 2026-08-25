export type RightsStatus = 
  | "SAFE_REUSE" 
  | "ATTRIBUTION_REQUIRED" 
  | "REVIEW_REQUIRED" 
  | "REFERENCE_ONLY" 
  | "BLOCKED";

export interface HealthData {
  status: "ok" | "degraded" | "error";
  service: string;
  environment: string;
  version: string;
  database: "connected" | "disconnected";
  timestamp: string;
}
