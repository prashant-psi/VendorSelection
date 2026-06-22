import { useRef, useState } from "react";
import { sendChatMessage } from "../api/chatApi";
import RankingTable from "./RankingTable";

const STARTER_PROMPTS = [
  "Suggest vendors for Resistors Grade-A PRD-00217, quantity 50",
  "Rank the best vendors for industrial bearings",
  "What can you help me with?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      text: "Hi! Ask me to suggest or rank vendors. Mention product name or code (e.g. PRD-00217) and quantity.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const listRef = useRef(null);

  const scrollToBottom = () => {
    requestAnimationFrame(() => {
      if (listRef.current) {
        listRef.current.scrollTop = listRef.current.scrollHeight;
      }
    });
  };

  const submitMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setError(null);
    setLoading(true);
    setMessages((prev) => [
      ...prev,
      { id: `user-${Date.now()}`, role: "user", text: trimmed },
    ]);
    setInput("");

    try {
      const response = await sendChatMessage({
        message: trimmed,
        ...(sessionId ? { session_id: sessionId } : {}),
      });

      setSessionId(response.session_id);
      setMessages((prev) => [
        ...prev,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: response.reply,
          data: response.data,
          actions: response.actions || [],
        },
      ]);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    submitMessage(input);
  };

  const handleNewChat = () => {
    setSessionId(null);
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        text: "Started a new conversation. How can I help with vendor selection?",
      },
    ]);
    setError(null);
  };

  return (
    <div className="chat-layout">
      <header className="chat-header">
        <div>
          <h1>Vendor Selection</h1>
          <p>Procurement assistant — chat powered by your backend API</p>
        </div>
        <button type="button" className="btn-secondary" onClick={handleNewChat}>
          New chat
        </button>
      </header>

      <main className="chat-main" ref={listRef}>
        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            <div className="message-label">
              {msg.role === "user" ? "You" : "Assistant"}
            </div>
            <div className="message-bubble">
              {msg.text.split("\n").map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
            {msg.actions?.length > 0 && (
              <div className="message-actions">
                {msg.actions.map((action) => (
                  <span key={action} className="badge">
                    {action}
                  </span>
                ))}
              </div>
            )}
            {msg.data && <RankingTable data={msg.data} />}
          </div>
        ))}

        {loading && (
          <div className="message message-assistant">
            <div className="message-label">Assistant</div>
            <div className="message-bubble typing">Thinking...</div>
          </div>
        )}
      </main>

      {error && <div className="error-banner">{error}</div>}

      <div className="starter-prompts">
        {STARTER_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            className="prompt-chip"
            disabled={loading}
            onClick={() => submitMessage(prompt)}
          >
            {prompt}
          </button>
        ))}
      </div>

      <form className="chat-input-row" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ask about vendors, rankings, or products..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn-primary" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
