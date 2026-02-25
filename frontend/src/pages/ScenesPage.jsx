import { useEffect, useState } from "react";
import { buildScenes, describeScene, getScene, listScenes } from "../api/scenes";
import { toAbsUrl } from "../api/client";

export default function ScenesPage({ jobId }) {
  const [scenes, setScenes] = useState([]);
  const [selectedSceneId, setSelectedSceneId] = useState("");

  const [sceneDetail, setSceneDetail] = useState(null);

  const [loading, setLoading] = useState(false);
  const [building, setBuilding] = useState(false);
  const [describing, setDescribing] = useState(false);
  const [error, setError] = useState("");

  async function refreshScenes() {
    if (!jobId) return;
    setLoading(true);
    setError("");
    try {
      const data = await listScenes(jobId);
      const list = data.scenes ?? [];
      setScenes(list);

      if (!selectedSceneId && list.length) {
        setSelectedSceneId(list[0].scene_id);
      }
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  async function loadScene(sceneId) {
    if (!jobId || !sceneId) return;
    setError("");
    try {
      const data = await getScene(jobId, sceneId, 8);
      setSceneDetail(data);
    } catch (e) {
      setError(String(e.message || e));
    }
  }

  async function onBuildScenes() {
    if (!jobId) return;
    setBuilding(true);
    setError("");
    try {
      await buildScenes(jobId);
      await refreshScenes();
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setBuilding(false);
    }
  }

async function onDescribe() {
  if (!jobId || !selectedSceneId) return;

  setDescribing(true);
  setError("");

  try {
    const updated = await describeScene(jobId, selectedSceneId, 8);

    // ✅ update right panel immediately
    setSceneDetail((prev) =>
      prev ? { ...prev, short_description: updated.short_description } : prev
    );

    // ✅ update left list immediately (main page list)
    setScenes((prev) =>
      prev.map((s) =>
        s.scene_id === selectedSceneId
          ? { ...s, short_description: updated.short_description }
          : s
      )
    );

    // (optional) also refresh from server for truth
    // await refreshScenes();
    // await loadScene(selectedSceneId);
  } catch (e) {
    setError(String(e.message || e));
  } finally {
    setDescribing(false);
  }
}

  // load list on job change
  useEffect(() => {
    setScenes([]);
    setSelectedSceneId("");
    setSceneDetail(null);
    if (jobId) refreshScenes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  // load detail when selection changes
  useEffect(() => {
    if (selectedSceneId) loadScene(selectedSceneId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedSceneId]);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 12 }}>
      {/* Left: scene list */}
      <div
        style={{
          border: "1px solid #eee",
          borderRadius: 12,
          padding: 12,
          background: "white",
          color: "#666"
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 8 }}>
          <h3 style={{ margin: 0 }}>Scenes</h3>
          <button
            onClick={onBuildScenes}
            disabled={building || !jobId}
            style={{
              padding: "6px 10px",
              borderRadius: 10,
              border: "1px solid #ddd",
              background: "white",
              cursor: building ? "not-allowed" : "pointer",
              color: "#666"
            }}
          >
            {building ? "Building…" : "Build scenes"}
          </button>
        </div>

        <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
          {loading ? "Loading…" : `${scenes.length} scene(s)`}
        </div>

        {error && <div style={{ marginTop: 8, fontSize: 12, color: "red" }}>{error}</div>}

        <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 8 }}>
          {scenes.map((s, idx) => {
            const active = s.scene_id === selectedSceneId;
            const title = `Scene ${idx + 1}`;
            const range = `${Number(s.start_sec).toFixed(1)}s – ${Number(s.end_sec).toFixed(1)}s`;

            return (
              <button
                key={s.scene_id}
                onClick={() => setSelectedSceneId(s.scene_id)}
                style={{
                  textAlign: "left",
                  padding: 10,
                  borderRadius: 12,
                  border: active ? "1px solid #bbb" : "1px solid #eee",
                  background: active ? "#f7f7f7" : "white",
                  cursor: "pointer",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{title}</div>
                  <div style={{ fontSize: 12, color: "#666" }}>{s.snapshot_count} snaps</div>
                </div>

                <div style={{ marginTop: 4, fontSize: 12, color: "#666" }}>{range}</div>

                {s.short_description && (
                  <div style={{ marginTop: 6, fontSize: 12, color: "#444" }}>
                    {s.short_description}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {!loading && scenes.length === 0 && (
          <div style={{ marginTop: 10, fontSize: 12, color: "#666" }}>
            No scenes yet. Click <b>Build scenes</b>.
          </div>
        )}
      </div>

      {/* Right: scene detail */}
      <div
        style={{
          border: "1px solid #eee",
          borderRadius: 12,
          padding: 12,
          background: "white",
        }}
      >
        {!sceneDetail && (
          <div style={{ color: "#666", fontSize: 13 }}>
            Select a scene to view keyframes.
          </div>
        )}

        {sceneDetail && (
          <>
            {/* Header row with describe button */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: 12,
                color: "#666"
              }}
            >
              <h3 style={{ margin: 0 }}>Keyframes</h3>

              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ fontSize: 12, color: "#666" }}>
                  {sceneDetail.keyframes_count} keyframes · {sceneDetail.snapshots_total} total
                </div>

                <button
                  onClick={onDescribe}
                  disabled={!selectedSceneId || describing}
                  style={{
                    padding: "6px 10px",
                    borderRadius: 10,
                    border: "1px solid #ddd",
                    background: "white",
                    cursor: "pointer",
                    color: "#666"
                  }}
                >
                  {describing ? "Describing…" : "Describe scene"}
                </button>
              </div>
            </div>

            <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
              {Number(sceneDetail.start_sec).toFixed(1)}s – {Number(sceneDetail.end_sec).toFixed(1)}s
            </div>

            {/* description */}
            <div style={{ marginTop: 10 }}>
              <div style={{ fontSize: 12, color: "#666" }}>Short description</div>
              <div style={{ marginTop: 4, fontSize: 13, color: "#333" }}>
                {sceneDetail.short_description ?? "(none)"}
              </div>
            </div>

            {/* keyframes grid */}
            <div
              style={{
                marginTop: 12,
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
                gap: 10,
              }}
            >
              {(sceneDetail.keyframes ?? []).map((k) => (
                <div
                  key={k.snapshot_id}
                  style={{
                    border: "1px solid #eee",
                    borderRadius: 12,
                    padding: 8,
                    background: "#fafafa",
                  }}
                >
                  <img
                    src={toAbsUrl(k.url)}
                    alt={`t=${k.timestamp_sec}s`}
                    style={{
                      width: "100%",
                      height: 120,
                      objectFit: "cover",
                      borderRadius: 10,
                      display: "block",
                      background: "white",
                    }}
                    loading="lazy"
                  />
                  <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                    {Number(k.timestamp_sec).toFixed(2)}s
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}