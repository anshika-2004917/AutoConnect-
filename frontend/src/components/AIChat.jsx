
import { useState, useRef, useEffect } from "react";
import API from "../services/api";
import "./AIChat.css";

export default function AIChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! 👋 I'm AutoConnect AI. Ask me about routes, stops, fares, autos, and available seats.",
    },
  ]);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading, isOpen]);

  const sendMessage = async (e) => {
    e.preventDefault();

    const question = message.trim();

    if (!question || loading) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await API.post("/ai/chat", {
        message: question,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            response.data.answer ||
            "I could not generate an answer.",
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            error.response?.data?.error ||
            "Sorry, I couldn't connect to AutoConnect AI. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-chat-container">

      {isOpen && (
        <div className="ai-chat-window">

          {/* Header */}
          <div className="ai-chat-header">
            <div className="ai-chat-brand">
              <div className="ai-chat-avatar">AI</div>

              <div>
                <h3>AutoConnect AI</h3>
                <span>Ask about your commute</span>
              </div>
            </div>

            <button
              className="ai-close-btn"
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="ai-chat-messages">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`ai-message-row ${msg.role}`}
              >
                <div className="ai-message-avatar">
                  {msg.role === "assistant" ? "AI" : "You"}
                </div>

                <div className="ai-message-bubble">
                  {msg.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="ai-message-row assistant">
                <div className="ai-message-avatar">AI</div>

                <div className="ai-message-bubble ai-typing">
                  AutoConnect AI is thinking...
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <form
            className="ai-chat-input-area"
            onSubmit={sendMessage}
          >
            <input
              type="text"
              placeholder="Ask anything about AutoConnect..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={loading}
            />

            <button
              type="submit"
              disabled={!message.trim() || loading}
              aria-label="Send message"
            >
              ➤
            </button>
          </form>

          <div className="ai-chat-footer">
            AutoConnect AI can make mistakes. Verify important details.
          </div>

        </div>
      )}

      {/* Floating Button */}
      <button
        className={`ai-floating-btn ${isOpen ? "active" : ""}`}
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label={isOpen ? "Close AI chat" : "Open AI chat"}
      >
        {isOpen ? "×" : "🤖"}
      </button>

    </div>
  );
}
