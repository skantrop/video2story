import { apiFetch } from "./client";

export async function buildScenes(jobId) {
  const res = await apiFetch(`/jobs/${jobId}/scenes/build`, { method: "POST" });
  return res.json();
}

export async function listScenes(jobId) {
  const res = await apiFetch(`/jobs/${jobId}/scenes`);
  return res.json();
}

export async function getScene(jobId, sceneId, keyframes = 8) {
  const res = await apiFetch(`/jobs/${jobId}/scenes/${sceneId}?keyframes=${keyframes}`);
  return res.json();
}