const { onRequest } = require("firebase-functions/v2/https");
const { defineSecret } = require("firebase-functions/params");
const logger = require("firebase-functions/logger");
const { GoogleGenerativeAI } = require("@google/generative-ai");
const cors = require("cors")({ origin: true });

// ✅ Attach the secret
const GEMINI_API_KEY = defineSecret("GEMINI_API_KEY");

exports.chat = onRequest(
  { region: "us-central1", secrets: [GEMINI_API_KEY] },
  async (req, res) => {
    cors(req, res, async () => {
      if (req.method === "OPTIONS") return res.status(204).send("");

      try {
        if (req.method !== "POST") {
          return res.status(405).json({ error: "Use POST" });
        }

        const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
        const { message } = body || {};

        if (!message || typeof message !== "string") {
          return res.status(400).json({ error: "Missing 'message' string" });
        }

        // ✅ Use the secret
        const genAI = new GoogleGenerativeAI(GEMINI_API_KEY.value());
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        const result = await model.generateContent(message);
        const reply = result.response.text();

        return res.status(200).json({ reply });
      } catch (e) {
        logger.error("Error in chat function", e);
        return res.status(500).json({ error: "Server error", detail: e.message || String(e) });
      }
    });
  }
);
