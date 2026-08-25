export type RightsStatus = 
  | 'SAFE_REUSE'
  | 'ATTRIBUTION_REQUIRED'
  | 'REVIEW_REQUIRED'
  | 'REFERENCE_ONLY'
  | 'BLOCKED';

export type MediaType = 'IMAGE' | 'VIDEO' | 'AUDIO';

export type QueryType = 
  | 'OFFICIAL'
  | 'EVENT'
  | 'COMPANY'
  | 'PERSON'
  | 'LOCATION'
  | 'CONCEPT'
  | 'BROLL';

export type RenderStatus = 
  | 'PENDING'
  | 'SYNTHESIZING_AUDIO'
  | 'PROCESSING_MEDIA'
  | 'RENDERING_VIDEO'
  | 'COMPLETED'
  | 'FAILED';

export interface HealthData {
  status: string;
  service: string;
  environment: string;
  version: string;
  database: string;
  timestamp: string;
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

export interface ProjectCreate {
  name: string;
  language?: string;
  script_raw?: string | null;
}

export interface ProjectUpdate {
  name?: string;
  language?: string;
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
  query?: string;
  query_type?: QueryType;
  priority?: number;
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
  metadata_json?: Record<string, any>;
  created_at: string;
}

export interface SelectedAsset {
  id: string;
  scene_id: string;
  media_candidate_id: string;
  order_index: number;
  framing_mode: string;
  notes?: string | null;
  created_at: string;
  media_candidate?: MediaCandidate | null;
}

export interface SelectedAssetCreate {
  media_candidate_id: string;
  order_index?: number;
  framing_mode?: string;
  notes?: string | null;
}

export interface SelectedAssetUpdate {
  order_index?: number;
  framing_mode?: string;
  notes?: string | null;
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
  selected_assets?: SelectedAsset[];
}

export interface SceneCreate {
  position?: number;
  title?: string | null;
  narration: string;
  visual_intent?: string | null;
  start_estimate?: number | null;
  end_estimate?: number | null;
}

export interface SceneUpdate {
  position?: number;
  title?: string | null;
  narration?: string;
  visual_intent?: string | null;
  start_estimate?: number | null;
  end_estimate?: number | null;
}

export interface SceneSplitRequest {
  first_part_narration: string;
  second_part_narration: string;
  first_part_title?: string;
  second_part_title?: string;
  first_part_visual_intent?: string;
  second_part_visual_intent?: string;
}

export interface SceneVisualPlanItem {
  scene_position: number;
  scene_title: string;
  narration: string;
  visual_intent?: string | null;
  start_estimate: number;
  end_estimate: number;
  duration: number;
  selected_asset?: SelectedAsset | null;
}

export interface VisualPlanExport {
  project_id: string;
  project_name: string;
  language: string;
  total_scenes: number;
  covered_scenes_count: number;
  total_duration_seconds: number;
  scenes: SceneVisualPlanItem[];
  consolidated_attributions: string[];
  markdown_document: string;
}

export interface RenderJob {
  id: string;
  project_id: string;
  status: RenderStatus;
  progress: number;
  aspect_ratio: string;
  voice: string;
  include_subtitles: boolean;
  include_credits_card: boolean;
  video_url?: string | null;
  duration_seconds?: number | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface RenderJobCreate {
  aspect_ratio?: string;
  voice?: string;
  include_subtitles?: boolean;
  include_credits_card?: boolean;
}

export interface VoiceOption {
  id: string;
  name: string;
}
