import { useEffect, useState } from "react";
import JobsSidebar from "../components/JobsSidebar";
import SnapshotsGrid from "../components/SnapshotsGrid";
import ScenesPage from "./ScenesPage";
import { listJobs, getJob, listSnapshots, deleteJob } from "../api/jobs";
import { getNarrative, generateNarrative } from "../api/narrative";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");

  const [detail, setDetail] = useState(null);
  const [snapshots, setSnapshots] = useState([]);

  const [loadingJobs, setLoadingJobs] = useState(false);
  const [error, setError] = useState("");

  const [tab, setTab] = useState("snapshots");

  const [narr, setNarr] = useState(null);
  const [narrLoading, setNarrLoading] = useState(false);
  const isFailed = detail?.status === "failed";

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
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "Something went wrong";

      setError(msg);
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
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "Something went wrong";

      setError(msg);
    }
  }

  async function loadNarrative(jobId) {
    if (!jobId) return;
    try {
      const res = await getNarrative(jobId);
      setNarr(res.narrative || null);
    } catch (e) {
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "Something went wrong";

      setError(msg);
    }
  }

  async function onGenerateNarrative() {
    if (!selectedJobId) return;
    setNarrLoading(true);
    setError("");
    try {
      const res = await generateNarrative(selectedJobId);
      setNarr(res.narrative || null);
      setTab("narrative");
    } catch (e) {
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "Something went wrong";

      setError(msg);
        setTab("narrative");

    } finally {
      setNarrLoading(false);
    }
  }

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
      setNarr(null);
      setTab("snapshots");

      if (nextId) {
        await loadDetailAndSnapshots(nextId);
      }
    } catch (e) {
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "Something went wrong";

      setError(msg);
    }
  }

  useEffect(() => {
    refreshJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!selectedJobId) return;
    setError("");
    setTab("snapshots");
    setDetail(null);
    setSnapshots([]);
    setNarr(null);
    loadDetailAndSnapshots(selectedJobId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedJobId]);

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

        {!selectedJobId && <div>Select a job</div>}

        {selectedJobId && (
          <>
            {detail && (
              <div style={{ marginBottom: 12 }}>
                <h2 style={{ marginBottom: 6 }}>Job detail</h2>
                <div style={{ fontSize: 13, color: "#555" }}>
                  <div>
                    <b>ID:</b> {detail.job_id}
                  </div>
                  <div>
                      <div>
                        <b>Status:</b>{" "}
                        <span
                          style={{
                            color:
                              detail.status === "completed"
                                ? "green"
                                : detail.status === "failed"
                                ? "red"
                                : detail.status === "processing"
                                ? "orange"
                                : "#555",
                            fontWeight: "bold",
                          }}
                        >
                          {detail.status}
                        </span>
                      </div>
                      {detail.error && (
                        <div style={{ color: "red", marginTop: 6 }}>
                          <b>Error:</b> {detail.error}
                        </div>
                      )}
                  </div>
                  <div>
                    <b>Snapshots:</b> {detail.snapshot_count}
                  </div>
                </div>
              </div>
            )}

            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
              <button
                onClick={() => setTab("snapshots")}
                style={{
                  padding: "6px 10px",
                  borderRadius: 10,
                  border: "1px solid #ddd",
                  background: tab === "snapshots" ? "#f3f3f3" : "white",
                  cursor: "pointer",
                  color: "#666",
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
                  background: tab === "scenes" ? "#f3f3f3" : "white",
                  cursor: "pointer",
                  color: "#666",

                }}
              >
                Scenes
              </button>

              <button
                onClick={() => {
                  setTab("narrative");
                  loadNarrative(selectedJobId);
                }}
                style={{
                  padding: "6px 10px",
                  borderRadius: 10,
                  border: "1px solid #ddd",
                  background: tab === "narrative" ? "#f3f3f3" : "white",
                  cursor: "pointer",
                  color: "#666",
                }}
              >
                Narrative
              </button>

              <div style={{ flex: 1 }} />

              <button
                onClick={onGenerateNarrative}
                disabled={narrLoading}
                style={{
                  padding: "6px 10px",
                  borderRadius: 10,
                  border: "1px solid #ddd",
                  background: narrLoading ? "#f3f3f3" : "white",
                  cursor: narrLoading ? "not-allowed" : "pointer",
                  color: "#666",
                }}
              >
                {narrLoading ? "Generating..." : "Generate narrative"}
              </button>
            </div>

            {tab === "snapshots" && <SnapshotsGrid snapshots={snapshots} />}

            {tab === "scenes" && <ScenesPage jobId={selectedJobId} />}

{tab === "narrative" && (
  <div>
    {error && (
      <div
        style={{
          background: "#fff4e5",
          border: "1px solid #ffcc80",
          padding: 10,
          borderRadius: 8,
          color: "#b26a00",
          marginBottom: 12,
        }}
      >
        <b>⚠️ Cannot generate narrative</b>
        <div style={{ marginTop: 4 }}>{error}</div>
      </div>
    )}
                {!narr && <div style={{ marginTop: 12, color: "#666" }}>No narrative yet.</div>}

                {narr && (
                <div style={{ marginTop: 12 }}>
                    <h3>Full story</h3>
                    <p style={{ whiteSpace: "pre-wrap" }}>{narr.full_story}</p>

                    <h3>Summary</h3>
                    <pre style={{ whiteSpace: "pre-wrap" }}>{narr.short_summary}</pre>

                    <h3>Structured</h3>
                    <pre style={{ whiteSpace: "pre-wrap" }}>
                    {JSON.stringify(narr.structured_data, null, 2)}
                    </pre>
                </div>
                )}
            </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}