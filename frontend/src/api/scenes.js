import { apiFetch } from "./client";

export async function buildScenes(jobId) {
  return await apiFetch(`/jobs/${jobId}/scenes/build`, { method: "POST" });
}

export async function listScenes(jobId) {
  return await apiFetch(`/jobs/${jobId}/scenes`);
}

export async function getScene(jobId, sceneId, keyframes = 8) {
  return await apiFetch(
    `/jobs/${jobId}/scenes/${sceneId}?keyframes=${keyframes}`
  );
}

export async function describeScene(jobId, sceneId, keyframes = 8) {
  return await apiFetch(
    `/jobs/${jobId}/scenes/${sceneId}/describe?keyframes=${keyframes}`,
    { method: "POST" }
  );
}