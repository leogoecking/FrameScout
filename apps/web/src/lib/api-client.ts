import { 
  HealthData, 
  Project, 
  ProjectCreate, 
  ProjectUpdate, 
  Scene, 
  SceneCreate, 
  SceneUpdate, 
  SceneSplitRequest 
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
