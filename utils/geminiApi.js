const axios = require("axios");

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent";

/**
 * Sends a prompt to Gemini API and returns the response.
 * @param {string} prompt
 * @returns {Promise<string>}
 */
async function getGeminiSuggestion(prompt) {
    try {
        const response = await axios.post(
            `${GEMINI_API_URL}?key=${GEMINI_API_KEY}`,
            {
                contents: [{ parts: [{ text: prompt }] }]
            }
        );
        return response.data.candidates[0]?.content?.parts[0]?.text || "";
    } catch (error) {
        console.error("Gemini API error:", error.message);
        return "Error fetching suggestion from Gemini.";
    }
}

module.exports = { getGeminiSuggestion };