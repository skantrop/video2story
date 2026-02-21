import { useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export default function App() {
  const [jobId, setJobId] = useState("");
  const [snapshots, setSnapshots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState("");

  const canRun = useMemo(() => jobId.trim().length > 0, [jobId]);

  async function loadSnapshots() {
    if (!canRun) return;
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}/snapshots`);
      if (!res.ok) throw new Error("Failed to fetch snapshots");
      const data = await res.json();
      setSnapshots(data.snapshots ?? []);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function runExtraction() {
    if (!canRun) return;
    setError("");
    setExtracting(true);

    try {
      await fetch(`${API_BASE}/jobs/${jobId}/extract`, { method: "POST" });
      setTimeout(loadSnapshots, 1500);
    } catch (e) {
      setError(String(e));
    } finally {
      setExtracting(false);
    }
  }

  function toUrl(u) {
    if (!u) return "";
    if (u.startsWith("http")) return u;
    return `${API_BASE}${u}`;
  }

  return (
    <div style={{ padding: 20, maxWidth: 1000, margin: "auto" }}>
      <h1>Video2Story Snapshots</h1>

      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <input
          value={jobId}
          onChange={(e) => setJobId(e.target.value)}
          placeholder="Enter job id"
          style={{ flex: 1, padding: 8 }}
        />

        <button onClick={loadSnapshots} disabled={!canRun || loading}>
          {loading ? "Loading..." : "Load"}
        </button>

        <button onClick={runExtraction} disabled={!canRun || extracting}>
          {extracting ? "Extracting..." : "Run extraction"}
        </button>
      </div>

      {error && <div style={{ color: "red" }}>{error}</div>}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: 10,
        }}
      >
        {snapshots.map((s) => (
          <div key={s.snapshot_id}>
            <img
              src={toUrl(s.url)}
              style={{ width: "100%" }}
              loading="lazy"
            />
            <div>{Number(s.timestamp_sec).toFixed(2)}s</div>
          </div>
        ))}
      </div>
    </div>
  );
}