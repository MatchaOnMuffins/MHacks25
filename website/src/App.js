import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [conversations, setConversations] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5001/api/feedback")
      .then((res) => res.json())
      .then((data) => setConversations(data))
      .catch((err) => console.error("Error fetching conversations:", err));
  }, []);

  const handleSelect = (conv) => {
    setSelected(conv);
  };

  const formatTimestamp = (ts) => {
    const date = new Date(ts * 1000); // Convert Unix timestamp
    return date.toLocaleString();
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <h2>Past Conversations</h2>
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className="conversation-item"
            onClick={() => handleSelect(conv)}
          >
            <p className="conversation-title">{formatTimestamp(conv.timestamp)}</p>
            <p className="conversation-summary">{conv.feedback.slice(0, 50)}...</p>
          </div>
        ))}
      </div>

      <div className="content">
        {selected ? (
          <div className="conversation-details">
            <h2>Conversation Details</h2>
            <section>
              <h3>Feedback</h3>
              <p>{selected.feedback}</p>
            </section>

            {selected.intermediate_feedbacks && selected.intermediate_feedbacks.length > 0 && (
              <section>
                <h3>Specific Feedbacks</h3>
                {JSON.parse(selected.intermediate_feedbacks).map((f, idx) => (
                  <div key={idx} className="specific-feedback">
                    <p>
                      <strong>Category:</strong> {f.category}
                    </p>
                    <p>
                      <strong>Total Score:</strong> {f.score}
                    </p>
                    <p>
                      <strong>Rubric Scores:</strong>{" "}
                      {Object.entries(f.rubric_scores)
                        .map(([k, v]) => `${k}: ${v}`)
                        .join(", ")}
                    </p>
                  </div>
                ))}
              </section>
            )}

            <section>
              <h3>Time Taken</h3>
              <p>{selected.time_taken || "N/A"} seconds</p>
            </section>
            <section>
              <h3>Timestamp</h3>
              <p>{formatTimestamp(selected.timestamp)}</p>
            </section>
          </div>
        ) : (
          <div className="conversation-details">
            <h2>Select a conversation to view details</h2>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
