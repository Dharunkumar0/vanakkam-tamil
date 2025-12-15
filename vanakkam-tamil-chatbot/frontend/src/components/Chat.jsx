import { useState, useRef, useEffect } from "react";
import { sendMessage } from "../api";
import Message from "./Message";
import TypingIndicator from "./TypingIndicator";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  async function handleSend() {
    if (!input.trim()) return;

    setError("");
    const userMsg = { role: "user", text: input };
    setMessages(m => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const reply = await sendMessage(input);
      setMessages(m => [...m, { role: "bot", text: reply }]);
    } catch (err) {
      const errorMsg = err.message || "சேவையக பிழை ஏற்பட்டுள்ளது. மீண்டும் முயற்சிக்கவும்.";
      setError(errorMsg);
      setMessages(m => [...m, { role: "error", text: errorMsg }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>🗣️ வணக்கம்</h2>
        <p>Tamil AI Assistant</p>
      </div>

      <div className="messages">
        {messages.length === 0 && (
          <div style={{ 
            textAlign: "center", 
            color: "#999", 
            marginTop: "auto", 
            marginBottom: "auto",
            padding: "20px"
          }}>
            <p style={{ fontSize: "48px", marginBottom: "10px" }}>🤖</p>
            <p>தமிழில் உங்கள் கேள்வி கேட்கவும்...</p>
          </div>
        )}
        {messages.map((m, i) => (
          <Message key={i} {...m} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-box">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="தமிழில் எழுதுங்கள்..."
          onKeyDown={e => e.key === "Enter" && !loading && handleSend()}
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          {loading ? "..." : "அனுப்பு"}
        </button>
      </div>
    </div>
  );
}
