import { useEffect, useState } from "react";

import JobsSidebar from "../components/JobsSidebar";
import SnapshotsGrid from "../components/SnapshotsGrid";

import { listJobs, getJob, listSnapshots, deleteJob } from "../api/jobs";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");

  const [detail, setDetail] = useState(null);
  const [snapshots, setSnapshots] = useState([]);

  const [loadingJobs, setLoadingJobs] = useState(false);
  const [error, setError] = useState("");

  // ---------- LOAD JOBS ----------
  async function refreshJobs() {
    setLoadingJobs(true);
    try {
      const data = await listJobs();
      const list = data.jobs ?? [];
      setJobs(list);

      if (!selectedJobId && list.length) {
        setSelectedJobId(list[0].job_id);
      }
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoadingJobs(false);
    }
  }

  // ---------- LOAD JOB DETAIL ----------
  async function loadDetail(jobId) {
    if (!jobId) return;
    try {
      const data = await getJob(jobId);
      setDetail(data);
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  // ---------- LOAD SNAPSHOTS ----------
  async function loadSnapshots(jobId) {
    if (!jobId) return;
    try {
      const data = await listSnapshots(jobId);
      setSnapshots(data.snapshots ?? []);
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  // ---------- DELETE JOB ----------
  async function onDelete(jobId) {
    if (!jobId) return;
    if (!confirm("Delete this job? This removes DB rows and files.")) return;

    setError("");

    try {
      await deleteJob(jobId);

      const data = await listJobs();
      const list = data.jobs ?? [];
      setJobs(list);

      const nextId = list.length ? list[0].job_id : "";
      setSelectedJobId(nextId);
      setDetail(null);
      setSnapshots([]);

      if (nextId) {
        await Promise.all([loadDetail(nextId), loadSnapshots(nextId)]);
      }
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  // ---------- EFFECTS ----------
  useEffect(() => {
    refreshJobs();
  }, []);

  useEffect(() => {
    if (selectedJobId) {
      loadDetail(selectedJobId);
      loadSnapshots(selectedJobId);
    }
  }, [selectedJobId]);

    useEffect(() => {
    if (!selectedJobId) return;

    let cancelled = false;
    let timerId = null;

    async function tick() {
        try {
        const d = await getJob(selectedJobId);
        if (cancelled) return;
        setDetail(d);

        // fetch snapshots too
        const s = await listSnapshots(selectedJobId);
        if (cancelled) return;
        setSnapshots(s.snapshots ?? []);

        // update sidebar counts/status
        const j = await listJobs();
        if (cancelled) return;
        setJobs(j.jobs ?? []);

        // keep polling while extracting/created/uploaded
        const stillRunning = ["created", "uploaded", "extracting"].includes(d.status);
        if (stillRunning) {
            timerId = setTimeout(tick, 1500);
        }
        } catch (e) {
        // don’t spam errors during polling; optional:
        // setError(String(e.message || e));
        }
    }

    tick();

    return () => {
        cancelled = true;
        if (timerId) clearTimeout(timerId);
    };
    }, [selectedJobId]);
  // ---------- UI ----------
  return (
    <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", height: "100vh" }}>
      {/* LEFT SIDEBAR */}
      <JobsSidebar
        jobs={jobs}
        selectedJobId={selectedJobId}
        onSelect={setSelectedJobId}
        onRefresh={refreshJobs}
        loading={loadingJobs}
        onDeleteJob={onDelete}   // ⭐ DELETE WIRED HERE
      />

      {/* RIGHT CONTENT */}
      <main style={{ padding: 16, overflow: "auto" }}>
        {error && (
          <div style={{ color: "red", marginBottom: 12 }}>
            {error}
          </div>
        )}

        {!selectedJobId && <div>Select a job</div>}

        {selectedJobId && (
          <>
            {/* DETAIL */}
            {detail && (
              <div style={{ marginBottom: 16 }}>
                <h2 style={{ marginBottom: 8 }}>Job detail</h2>

                <div style={{ fontSize: 13, color: "#555" }}>
                  <div><b>ID:</b> {detail.job_id}</div>
                  <div><b>Status:</b> {detail.status}</div>
                  <div><b>Snapshots:</b> {detail.snapshot_count}</div>
                </div>
              </div>
            )}

            {/* SNAPSHOTS */}
            <SnapshotsGrid snapshots={snapshots} />
          </>
        )}
      </main>
    </div>
  );
}
