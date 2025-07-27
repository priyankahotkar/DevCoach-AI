const express = require("express");
const axios = require("axios");
const router = express.Router();

// Example: /api/codeforces/user/Priyanka_2004
router.get("/user/:handle", async (req, res) => {
    const { handle } = req.params;
    try {
        const response = await axios.get(`https://codeforces.com/api/user.status?handle=${handle}`);
        res.json(response.data.result);
    } catch (error) {
        res.status(500).json({ error: "Codeforces API error" });
    }
});

module.exports = router;
