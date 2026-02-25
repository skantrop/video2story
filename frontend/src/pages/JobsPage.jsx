import { useEffect, useMemo, useState } from "react";

import JobsSidebar from "../components/JobsSidebar";
import SnapshotsGrid from "../components/SnapshotsGrid";
import ScenesPage from "./ScenesPage";

import { listJobs, getJob, listSnapshots, deleteJob } from "../api/jobs";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");

  const [detail, setDetail] = useState(null);
  const [snapshots, setSnapshots] = useState([]);

  const [loadingJobs, setLoadingJobs] = useState(false);
  const [error, setError] = useState("");

  const [tab, setTab] = useState("snapshots");

  // ---------- helpers ----------
  const isRunning = useMemo(() => {
    const st = detail?.status;
    return st && ["created", "uploaded", "extracting"].includes(st);
  }, [detail?.status]);

  async function refreshJobs() {
    setLoadingJobs(true);
    try {
      const data = await listJobs();
      const list = data.jobs ?? [];
      setJobs(list);

      // auto-select first if none selected
      if (!selectedJobId && list.length) {
        setSelectedJobId(list[0].job_id);
      }
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoadingJobs(false);
    }
  }

  async function loadDetailAndSnapshots(jobId) {
    if (!jobId) return;
    try {
      const [d, s] = await Promise.all([getJob(jobId), listSnapshots(jobId)]);
      setDetail(d);
      setSnapshots(s.snapshots ?? []);
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  // ---------- delete ----------
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
      setTab("snapshots");

      if (nextId) {
        await loadDetailAndSnapshots(nextId);
      }
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  // ---------- initial load ----------
  useEffect(() => {
    refreshJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------- when selection changes: load once + reset tab ----------
  useEffect(() => {
    if (!selectedJobId) return;
    setError("");
    setTab("snapshots");
    setDetail(null);
    setSnapshots([]);
    loadDetailAndSnapshots(selectedJobId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedJobId]);


  // ---------- UI ----------
  return (
    <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", height: "100vh" }}>
      <JobsSidebar
        jobs={jobs}
        selectedJobId={selectedJobId}
        onSelect={setSelectedJobId}
        onRefresh={refreshJobs}
        loading={loadingJobs}
        onDeleteJob={onDelete}
      />

      <main style={{ padding: 16, overflow: "auto" }}>
        {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}

        {!selectedJobId && <div>Select a job</div>}

        {selectedJobId && (
          <>
            {/* DETAIL */}
            {detail && (
              <div style={{ marginBottom: 12 }}>
                <h2 style={{ marginBottom: 6 }}>Job detail</h2>
                <div style={{ fontSize: 13, color: "#555" }}>
                  <div>
                    <b>ID:</b> {detail.job_id}
                  </div>
                  <div>
                    <b>Status:</b> {detail.status}
                  </div>
                  <div>
                    <b>Snapshots:</b> {detail.snapshot_count}
                  </div>
                </div>
              </div>
            )}

            {/* TABS */}
            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
              <button
                onClick={() => setTab("snapshots")}
                style={{
                  padding: "6px 10px",
                  borderRadius: 10,
                  border: "1px solid #ddd",
                  background: tab === "snapshots" ? "#f3f3f3" : "#908f8f",
                  color: "#666",
                  cursor: "pointer",
                }}
              >
                Snapshots
              </button>

              <button
                onClick={() => setTab("scenes")}
                style={{
                  padding: "6px 10px",
                  borderRadius: 10,
                  border: "1px solid #ddd",
                  background: tab === "scenes" ? "#f3f3f3" : "#908f8f",
                  color: "#666",
                  cursor: "pointer",
                }}
              >
                Scenes
              </button>
            </div>

            {/* CONTENT */}
            {tab === "snapshots" && <SnapshotsGrid snapshots={snapshots} />}

            {tab === "scenes" && <ScenesPage jobId={selectedJobId} />}
          </>
        )}
      </main>
    </div>
  );
}