import { API_BASE } from "../api/client";

function toAbsoluteUrl(u) {
  if (!u) return "";
  if (u.startsWith("http")) return u;
  return `${API_BASE}${u}`;
}

export default function SnapshotsGrid({ snapshots }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 10 }}>
      {snapshots.map((s) => (
        <div key={s.snapshot_id} style={{ border: "1px solid #eee", borderRadius: 12, overflow: "hidden" }}>
          <img src={toAbsoluteUrl(s.url)} alt={`t=${s.timestamp_sec}`} style={{ width: "100%", display: "block" }} loading="lazy" />
          <div style={{ padding: 8, fontSize: 12, display: "flex", justifyContent: "space-between" }}>
            <b>{Number(s.timestamp_sec).toFixed(2)}s</b>
            <span style={{ color: "#777" }}>{s.width}×{s.height}</span>
          </div>
        </div>
      ))}
    </div>
  );
}