import { apiFetch } from "./client";

export async function generateNarrative(jobId) {
  return await apiFetch(`/jobs/${jobId}/narrative/generate`, {
    method: "POST",
  });
}

export async function getNarrative(jobId) {
  return await apiFetch(`/jobs/${jobId}/narrative`);
}