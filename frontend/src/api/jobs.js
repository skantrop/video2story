import { apiFetch } from "./client";

export async function listJobs() {
  return await apiFetch("/jobs");
}

export async function getJob(jobId) {
  return await apiFetch(`/jobs/${jobId}`);
}

export async function listSnapshots(jobId, { limit, offset } = {}) {
  const qs = new URLSearchParams();
  if (limit != null) qs.set("limit", String(limit));
  if (offset != null) qs.set("offset", String(offset));
  const suffix = qs.toString() ? `?${qs.toString()}` : "";

  return await apiFetch(`/jobs/${jobId}/snapshots${suffix}`);
}

export async function runExtract(jobId) {
  return await apiFetch(`/jobs/${jobId}/extract`, { method: "POST" });
}

export async function createJob(formData) {
  return await apiFetch("/jobs", { method: "POST", body: formData });
}

export async function deleteJob(jobId) {
  return await apiFetch(`/jobs/${jobId}`, { method: "DELETE" });
}