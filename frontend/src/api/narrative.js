import { apiFetch } from "./client";

export async function getNarrative(jobId) {
  const res = await apiFetch(`/jobs/${jobId}/narrative`);
  return await res.json();
}

export async function generateNarrative(jobId) {
  const res = await apiFetch(`/jobs/${jobId}/narrative/generate`, { method: "POST" });
  return await res.json();
}