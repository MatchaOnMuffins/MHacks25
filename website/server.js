const express = require("express");
const mysql = require("mysql2/promise");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// --- MySQL Connection ---
const pool = mysql.createPool({
  host: "34.56.161.151",
  user: "root",     
  password: 's1Ii4\\4+UJlL;R\\R',
  database: "feedback_db",
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// --- Get past conversations ---
app.get("/api/feedback", async (req, res) => {
  try {
    const [rows] = await pool.query(
      "SELECT * FROM feedback ORDER BY timestamp DESC"
    );
    
    // Map to UI-friendly format
    const conversations = rows.map(row => ({
      id: row.id,
      feedback: row.feedback,
      intermediate_feedbacks: row.intermediate_feedbacks,
      timestamp: row.timestamp,
      time_taken: row.time_taken
    }));

    res.json(conversations);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to fetch conversations" });
  }
});

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
