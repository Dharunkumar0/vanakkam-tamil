export default function Message({ role, text }) {
  const className = role === "user" ? "user" : role === "error" ? "error-message" : "bot";
  return <div className={`message ${className}`}>{text}</div>;
}
