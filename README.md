# DevCoach-AI

DevCoach-AI is an AI-powered coding mentor platform that integrates LeetCode, GitHub, and Codeforces APIs.
It provides real-time, personalized insights, recommendations, and learning roadmaps for developers.

---

## Features

- **User Progress Tracking**: Fetches and analyzes user activity from LeetCode, GitHub, and Codeforces.
- **AI-Powered Suggestions**: Personalized coding practice and learning recommendations.
- **Dashboard**: Interactive frontend to visualize progress and get tailored insights.
- **Full-Stack Architecture**: React.js frontend + Python (FastAPI/Flask) backend.

---

## Tech Stack

- **Frontend**: React.js, Tailwind CSS
- **Backend**: Python (FastAPI/Flask)
- **Database**: MongoDB
- **APIs Integrated**: LeetCode, GitHub, Codeforces
- **Deployment**: Docker / Vercel (frontend) + Render/Heroku (backend)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/priyankahotkar/DevCoach-AI.git
cd DevCoach-AI
```

### 2. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the backend server:

```bash
uvicorn main:app --reload
```

Backend will run at `http://127.0.0.1:8000/`

### 3. Setup Frontend

```bash
cd frontend
npm install
npm start
```

Frontend will run at `http://localhost:3000/`

---

## Running the Application

- Start **backend** server first (FastAPI/Flask).
- Then start **frontend** (React).
- Open browser at `http://localhost:3000/`.

---

## Deployment

### Frontend

- Deploy React app on **Vercel** or **Netlify**.

### Backend

- Use **Render**, **Heroku**, or **AWS EC2**.
- Containerize using Docker for easier deployment:

```bash
docker build -t devcoach-backend .
docker run -p 8000:8000 devcoach-backend
```

---

## Testing

### Backend Tests

```bash
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Roadmap

- Add AI-based personalized coding roadmap generation.
- Enhance leaderboard & social features.
- Integrate authentication (Google/GitHub login).

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss.

---
