import { 
  HealthData, 
  MediaCandidate,
  Project, 
  ProjectCreate, 
  ProjectUpdate, 
  Scene, 
  SceneCreate, 
  SceneUpdate, 
  SceneSplitRequest,
  SearchQuery,
  SearchQueryCreate,
  SearchQueryUpdate,
  SelectedAsset,
  SelectedAssetCreate,
  SelectedAssetUpdate,
  VisualPlanExport, RenderJob, RenderJobCreate, VoiceOption, ProjectFidelityMetrics,
  SceneEntitiesResponse, ProjectEntitiesResponse,
  GenerateScriptRequest, GenerateScriptResponse
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function parseErrorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const data: { detail?: string | Array<{ msg?: string }> } = await res.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((d: { msg?: string }) => d.msg || JSON.stringify(d)).join(", ");
    }
    return fallback;
  } catch {
    return fallback;
  }
}

export async function fetchHealth(): Promise<HealthData> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Health check failed with status: ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    return {
      status: "error",
      service: "api",
      environment: "unknown",
      version: "0.1.0",
      database: "disconnected",
      timestamp: new Date().toISOString(),
    };
  }
}

// --- Projects ---

export async function listProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to list projects: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function getProject(id: string): Promise<Project> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${id}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to get project: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function createProject(data: ProjectCreate): Promise<Project> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to create project: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function updateProject(id: string, data: ProjectUpdate): Promise<Project> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to update project: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function deleteProject(id: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${id}`, {
    method: "DELETE",
  });
  if (!res.ok && res.status !== 204) {
    const msg = await parseErrorMessage(res, `Failed to delete project: ${res.status}`);
    throw new Error(msg);
  }
}

// --- Scenes ---

export async function listScenes(projectId: string): Promise<Scene[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/scenes`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to list scenes: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function generateScenes(projectId: string): Promise<Scene[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/scenes/generate`, {
    method: "POST",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to generate scenes: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function createScene(projectId: string, data: SceneCreate): Promise<Scene> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/scenes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to create scene: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function updateScene(sceneId: string, data: SceneUpdate): Promise<Scene> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to update scene: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function deleteScene(sceneId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}`, {
    method: "DELETE",
  });
  if (!res.ok && res.status !== 204) {
    const msg = await parseErrorMessage(res, `Failed to delete scene: ${res.status}`);
    throw new Error(msg);
  }
}

export async function reorderScenes(projectId: string, sceneIds: string[]): Promise<Scene[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/scenes/reorder`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scene_ids: sceneIds }),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to reorder scenes: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function splitScene(sceneId: string, data: SceneSplitRequest): Promise<Scene[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/split`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to split scene: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function mergeScenes(sceneId: string, targetSceneId: string): Promise<Scene> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/merge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_scene_id: targetSceneId }),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to merge scenes: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

// --- Search Queries ---

export async function listQueries(sceneId: string): Promise<SearchQuery[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/queries`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to list queries: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function generateSceneQueries(sceneId: string): Promise<SearchQuery[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/queries/generate`, {
    method: "POST",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to generate scene queries: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function generateProjectQueries(
  projectId: string
): Promise<{ scenes_count: number; total_queries_created: number }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/queries/generate`, {
    method: "POST",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to generate project queries: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function createQuery(
  sceneId: string,
  data: SearchQueryCreate
): Promise<SearchQuery> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/queries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to create query: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function updateQuery(
  queryId: string,
  data: SearchQueryUpdate
): Promise<SearchQuery> {
  const res = await fetch(`${API_BASE_URL}/api/v1/queries/${queryId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to update query: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function deleteQuery(queryId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/queries/${queryId}`, {
    method: "DELETE",
  });
  if (!res.ok && res.status !== 204) {
    const msg = await parseErrorMessage(res, `Failed to delete query: ${res.status}`);
    throw new Error(msg);
  }
}

// --- Media Candidates (Pexels + Wikimedia Commons) ---

export async function searchQueryMedia(
  queryId: string,
  provider?: string,
  limit: number = 8
): Promise<MediaCandidate[]> {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (provider) {
    params.set("provider", provider);
  }

  const res = await fetch(`${API_BASE_URL}/api/v1/queries/${queryId}/search?${params.toString()}`, {
    method: "POST",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to search query media: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function searchSceneMedia(
  sceneId: string,
  provider?: string,
  limitPerQuery: number = 4
): Promise<MediaCandidate[]> {
  const params = new URLSearchParams({ limit_per_query: limitPerQuery.toString() });
  if (provider) {
    params.set("provider", provider);
  }

  const res = await fetch(
    `${API_BASE_URL}/api/v1/scenes/${sceneId}/search?${params.toString()}`,
    {
      method: "POST",
    }
  );
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to search scene media: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function listSceneCandidates(sceneId: string): Promise<MediaCandidate[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/candidates`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to list scene candidates: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function listQueryCandidates(queryId: string): Promise<MediaCandidate[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/queries/${queryId}/candidates`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to list query candidates: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function getCandidate(candidateId: string): Promise<MediaCandidate> {
  const res = await fetch(`${API_BASE_URL}/api/v1/candidates/${candidateId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to get candidate: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

// --- Selected Assets & Visual Plan ---

export async function selectAssetForScene(
  sceneId: string,
  data: SelectedAssetCreate
): Promise<SelectedAsset> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/assets/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to select asset: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function listSceneSelectedAssets(sceneId: string): Promise<SelectedAsset[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/assets`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to list selected assets: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function updateSelectedAsset(
  assetId: string,
  data: SelectedAssetUpdate
): Promise<SelectedAsset> {
  const res = await fetch(`${API_BASE_URL}/api/v1/selected-assets/${assetId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to update selected asset: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function removeSelectedAsset(assetId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/selected-assets/${assetId}`, {
    method: "DELETE",
  });
  if (!res.ok && res.status !== 204) {
    const msg = await parseErrorMessage(res, `Failed to remove selected asset: ${res.status}`);
    throw new Error(msg);
  }
}

export async function exportProjectVisualPlan(projectId: string): Promise<VisualPlanExport> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/visual-plan`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to export visual plan: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

// --- Video Rendering Engine (Studio) ---

export async function listAvailableVoices(): Promise<VoiceOption[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/voices`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to list voices: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function triggerRenderJob(
  projectId: string,
  data: RenderJobCreate = {}
): Promise<RenderJob> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/render`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to trigger render: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function listProjectRenderJobs(projectId: string): Promise<RenderJob[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/render-jobs`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to list render jobs: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function getRenderJob(jobId: string): Promise<RenderJob> {
  const res = await fetch(`${API_BASE_URL}/api/v1/render-jobs/${jobId}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to get render job: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export function getRenderVideoStreamUrl(jobId: string): string {
  return `${API_BASE_URL}/api/v1/render-jobs/${jobId}/stream`;
}

// --- Semantic Ranking & Fidelity Score ---

export async function rerankSceneCandidates(sceneId: string): Promise<MediaCandidate[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/rerank`, {
    method: "POST",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to rerank scene candidates: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function getProjectFidelityMetrics(projectId: string): Promise<ProjectFidelityMetrics> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/fidelity-metrics`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to get project fidelity metrics: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

// --- Entity Extraction (Sprint 13) ---

export async function extractSceneEntities(sceneId: string): Promise<SceneEntitiesResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/entities/extract`, {
    method: "POST",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to extract scene entities: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function extractProjectEntities(projectId: string): Promise<ProjectEntitiesResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/entities/extract`, {
    method: "POST",
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to extract project entities: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

// --- AI Media Generation (Gemini / Imagen 3) ---

export async function generateSceneAIImage(
  sceneId: string,
  data?: { prompt?: string; aspect_ratio?: string; count?: number }
): Promise<MediaCandidate[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/scenes/${sceneId}/ai/generate-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data || {}),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to generate AI image: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

// --- AI Script Generator (Gemini Copilot) ---

export async function generateScript(
  data: GenerateScriptRequest
): Promise<GenerateScriptResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/generate-script`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to generate script: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}

export async function generateProjectScript(
  projectId: string,
  data: GenerateScriptRequest
): Promise<GenerateScriptResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/projects/${projectId}/generate-script`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const msg = await parseErrorMessage(res, `Failed to generate project script: ${res.status}`);
    throw new Error(msg);
  }
  return await res.json();
}



