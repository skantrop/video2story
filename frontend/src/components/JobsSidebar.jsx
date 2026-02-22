import StatusBadge from "./StatusBadge";

function formatDate(iso) {
  if (!iso) return "";
  try { return new Date(iso).toLocaleString(); } catch { return iso; }
}

export default function JobsSidebar({ jobs, selectedJobId, onSelect, onRefresh, loading }) {
  return (
    <aside style={{ borderRight: "1px solid #eee", padding: 12, background: "#fafafa", overflow: "auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0, fontSize: 18 }}>Jobs</h2>
        <button onClick={onRefresh} disabled={loading}
          style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #ddd", background: "white" }}>
          {loading ? "…" : "Refresh"}
        </button>
      </div>

      <div style={{ marginTop: 8, color: "#666", fontSize: 12 }}>{jobs.length} job(s)</div>

      <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 8 }}>
        {jobs.map((j) => {
          const active = j.job_id === selectedJobId;
          return (
            <button
              key={j.job_id}
              onClick={() => onSelect(j.job_id)}
              style={{
                textAlign: "left",
                padding: 10,
                borderRadius: 12,
                border: active ? "1px solid #bbb" : "1px solid #e6e6e6",
                background: "white",
                cursor: "pointer",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                <div style={{ fontSize: 12, color: "#444", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {j.job_id}
                </div>
                <StatusBadge status={j.status} />
              </div>
              <div style={{ marginTop: 6, display: "flex", justifyContent: "space-between", fontSize: 12, color: "#666" }}>
                <span>{formatDate(j.created_at)}</span>
                <span>{j.snapshot_count} snaps</span>
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}