const express = require("express");
const axios = require("axios");
const router = express.Router();

// Endpoint: GET /api/leetcode/user/:username
router.get("/user/:username", async (req, res) => {
    const { username } = req.params;

    try {
        const response = await axios.get(`https://leetcode-api-faisalshohag.vercel.app/${username}`);
        const data = response.data;

        // Optional: format or clean the response before sending
        const userStats = {
            username,
            totalSolved: data.totalSolved,
            easySolved: data.easySolved,
            mediumSolved: data.mediumSolved,
            hardSolved: data.hardSolved,
            ranking: data.ranking,
            recentSubmissions: data.recentSubmissions,
            submissionCalendar: data.submissionCalendar,
            acceptanceRates: {
                easy: `${(data.matchedUserStats.acSubmissionNum[1].count / data.matchedUserStats.totalSubmissionNum[1].submissions * 100).toFixed(2)}%`,
                medium: `${(data.matchedUserStats.acSubmissionNum[2].count / data.matchedUserStats.totalSubmissionNum[2].submissions * 100).toFixed(2)}%`,
                hard: `${(data.matchedUserStats.acSubmissionNum[3].count / data.matchedUserStats.totalSubmissionNum[3].submissions * 100).toFixed(2)}%`
            }
        };

        res.json(userStats);

    } catch (error) {
        console.error("LeetCode API error:", error.message);
        res.status(500).json({ error: "Failed to fetch data from LeetCode API" });
    }
});

module.exports = router;
