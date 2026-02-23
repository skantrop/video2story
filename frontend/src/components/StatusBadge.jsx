export default function StatusBadge({ status }) {
  const label = status || "unknown";
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 999,
        border: "1px solid #ddd",
        fontSize: 12,
        background: "#fafafa",
        color: "#666",
      }}
    >
      {label}
    </span>
  );
}