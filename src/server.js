const express = require("express");
const cors = require("cors");
const app = express();

app.use(cors());
app.use(express.json());

const githubRoutes = require("../routes/github");
const codeforcesRoutes = require("../routes/codeforces");
const leetcodeRoutes = require("../routes/leetcode");
const agentRoutes = require("../routes/agent");

app.use("/api/github", githubRoutes);
app.use("/api/codeforces", codeforcesRoutes);
app.use("/api/leetcode", leetcodeRoutes);
app.use("/agent", agentRoutes);

app.get("/", (req, res) => {
    res.send("Welcome to the API!");
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
