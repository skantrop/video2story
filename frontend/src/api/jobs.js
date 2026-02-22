import { apiFetch } from "./client";

export async function listJobs() {
  const res = await apiFetch("/jobs");
  return res.json();
}

export async function getJob(jobId) {
  const res = await apiFetch(`/jobs/${jobId}`);
  return res.json();
}

export async function listSnapshots(jobId, { limit, offset } = {}) {
  const qs = new URLSearchParams();
  if (limit != null) qs.set("limit", String(limit));
  if (offset != null) qs.set("offset", String(offset));
  const suffix = qs.toString() ? `?${qs.toString()}` : "";
  const res = await apiFetch(`/jobs/${jobId}/snapshots${suffix}`);
  return res.json();
}

export async function runExtract(jobId) {
  const res = await apiFetch(`/jobs/${jobId}/extract`, { method: "POST" });
  return res.json();
}

export async function createJob(formData) {
  const res = await apiFetch("/jobs", { method: "POST", body: formData });
  return res.json();
}