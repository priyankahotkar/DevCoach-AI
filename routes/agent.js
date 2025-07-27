const express = require("express");
const axios = require("axios");
const { getGeminiSuggestion } = require("../utils/geminiApi");
const router = express.Router();

// GET /api/agent/suggest/:username/:handle
router.get("/suggest/:username/:handle", async (req, res) => {
    const { username, handle } = req.params;

    try {
        // Fetch user activity from GitHub, LeetCode, and Codeforces
        const [githubRes, leetcodeRes, codeforcesRes] = await Promise.all([
            axios.get(`http://localhost:3000/api/github/user/${username}`),
            axios.get(`http://localhost:3000/api/leetcode/user/${username}`),
            axios.get(`http://localhost:3000/api/codeforces/user/${handle}`)
        ]);

        // Build a prompt for Gemini
        const prompt = `
GitHub activity: ${JSON.stringify(githubRes.data)}
LeetCode stats: ${JSON.stringify(leetcodeRes.data)}
Codeforces submissions: ${JSON.stringify(codeforcesRes.data)}
Based on this, suggest what the user should do next to improve their skills.
        `;

        // Get suggestion from Gemini
        const suggestion = await getGeminiSuggestion(prompt);

        res.json({ suggestion });
    } catch (error) {
        res.status(500).json({ error: "Failed to generate suggestion." });
    }
});

module.exports = router;