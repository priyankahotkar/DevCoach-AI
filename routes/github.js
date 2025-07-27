const express = require("express");
const axios = require("axios");
const router = express.Router();

// Example: /api/github/user/priyankahotkar
router.get("/user/:username", async (req, res) => {
    const { username } = req.params;
    try {
        const response = await axios.get(`https://api.github.com/users/${username}/events/public`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: "GitHub API error" });
    }
});

module.exports = router;
