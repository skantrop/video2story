import { useEffect, useState } from "react";
import JobsSidebar from "../components/JobsSidebar";
import SnapshotsGrid from "../components/SnapshotsGrid";
import StatusBadge from "../components/StatusBadge";
import { getJob, listJobs, listSnapshots, runExtract } from "../api/jobs";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [detail, setDetail] = useState(null);
  const [snapshots, setSnapshots] = useState([]);

  const [loadingJobs, setLoadingJobs] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [loadingSnaps, setLoadingSnaps] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState("");

  async function refreshJobs() {
    setError("");
    setLoadingJobs(true);
    try {
      const data = await listJobs();
      const list = data.jobs ?? [];
      setJobs(list);
      if (!selectedJobId && list.length) setSelectedJobId(list[0].job_id);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoadingJobs(false);
    }
  }

  async function loadDetail(jobId) {
    if (!jobId) return;
    setError("");
    setLoadingDetail(true);
    try {
      const data = await getJob(jobId);
      setDetail(data);
    } catch (e) {
      setError(String(e.message || e));
      setDetail(null);
    } finally {
      setLoadingDetail(false);
    }
  }

  async function loadSnapshots(jobId) {
    if (!jobId) return;
    setError("");
    setLoadingSnaps(true);
    try {
      const data = await listSnapshots(jobId);
      setSnapshots(data.snapshots ?? []);
    } catch (e) {
      setError(String(e.message || e));
      setSnapshots([]);
    } finally {
      setLoadingSnaps(false);
    }
  }

  async function onExtract(jobId) {
    if (!jobId) return;
    setError("");
    setExtracting(true);
    try {
      await runExtract(jobId);
      await new Promise((r) => setTimeout(r, 1200));
      await Promise.all([refreshJobs(), loadDetail(jobId), loadSnapshots(jobId)]);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setExtracting(false);
    }
  }

  useEffect(() => { refreshJobs(); }, []);
  useEffect(() => {
    if (!selectedJobId) return;
    loadDetail(selectedJobId);
    loadSnapshots(selectedJobId);
  }, [selectedJobId]);

  return (
    <div style={{ height: "100vh", display: "grid", gridTemplateColumns: "320px 1fr", fontFamily: "system-ui" }}>
      <JobsSidebar
        jobs={jobs}
        selectedJobId={selectedJobId}
        onSelect={setSelectedJobId}
        onRefresh={refreshJobs}
        loading={loadingJobs}
      />

      <main style={{ padding: 16, overflow: "auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 22 }}>Job workspace</h1>
            <div style={{ marginTop: 6, color: "#666" }}>
              {selectedJobId ? <>Selected: <code>{selectedJobId}</code></> : "Select a job"}
            </div>
          </div>

          <div style={{ display: "flex", gap: 8 }}>
            <button
              onClick={() => onExtract(selectedJobId)}
              disabled={!selectedJobId || extracting}
              style={{ padding: "8px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white" }}
            >
              {extracting ? "Extracting…" : "Run extraction"}
            </button>
            <button
              onClick={() => selectedJobId && Promise.all([loadDetail(selectedJobId), loadSnapshots(selectedJobId)])}
              disabled={!selectedJobId || loadingDetail || loadingSnaps}
              style={{ padding: "8px 12px", borderRadius: 10, border: "1px solid #ddd", background: "white" }}
            >
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: 12, padding: 12, borderRadius: 10, border: "1px solid #f5c2c7", background: "#f8d7da" }}>
            {error}
          </div>
        )}

        <section style={{ marginTop: 14, padding: 14, borderRadius: 14, border: "1px solid #eee", background: "white" }}>
          <h3 style={{ marginTop: 0 }}>Overview</h3>
          {!selectedJobId ? (
            <div style={{ color: "#666" }}>Select a job.</div>
          ) : loadingDetail ? (
            <div style={{ color: "#666" }}>Loading…</div>
          ) : !detail ? (
            <div style={{ color: "#666" }}>No detail.</div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <div>
                <div style={{ color: "#666", fontSize: 12 }}>Status</div>
                <div style={{ marginTop: 4 }}><StatusBadge status={detail.status} /></div>
              </div>
              <div>
                <div style={{ color: "#666", fontSize: 12 }}>Snapshots</div>
                <div style={{ marginTop: 4 }}>{detail.snapshot_count}</div>
              </div>
              <div style={{ gridColumn: "1 / -1" }}>
                <div style={{ color: "#666", fontSize: 12, marginBottom: 6 }}>Config</div>
                <pre style={{ margin: 0, padding: 10, borderRadius: 10, background: "#f7f7f7", border: "1px solid #eee", fontSize: 12 }}>
                  {JSON.stringify(detail.config, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </section>

        <section style={{ marginTop: 14 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <h3 style={{ margin: 0 }}>Snapshots</h3>
            <div style={{ color: "#666", fontSize: 12 }}>{loadingSnaps ? "Loading…" : `${snapshots.length} frame(s)`}</div>
          </div>

          <div style={{ marginTop: 10 }}>
            {snapshots.length === 0 && !loadingSnaps ? (
              <div style={{ color: "#666" }}>No snapshots yet. Click “Run extraction”.</div>
            ) : (
              <SnapshotsGrid snapshots={snapshots} />
            )}
          </div>
        </section>
      </main>
    </div>
  );
}