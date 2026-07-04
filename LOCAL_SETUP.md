# 🛠️ Local Development & Deployment Guide

This guide provides step-by-step instructions for spinning up the Graphical Password Authentication (GPA) system on your local machine for development and testing.

## Prerequisites

Ensure you have the following installed on your system:
- **Python 3.11+** (Backend runtime)
- **Node.js 18+** (Frontend build and dev server)
- **Redis 7+** (Optional but recommended for challenge/rate-limit storage. The system falls back to in-memory dictionaries if Redis is unavailable).
- **Git**

---

## 1. Repository Setup

Clone the repository and navigate to the project root:

```bash
git clone https://github.com/ShadyNights/Graphical-Password-Authentication.git
cd Graphical-Password-Authentication
```

---

## 2. Backend Configuration

The backend is a FastAPI application. We recommend using a virtual environment.

### Installation
```bash
cd backend
python -m venv venv

# Activate the environment (Windows)
venv\Scripts\activate
# Activate the environment (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file inside the `backend/` directory:

```env
# Database (Defaults to local SQLite)
DATABASE_URL=sqlite+aiosqlite:///./gpa_dev.db

# Redis (Update if using a different port or Docker)
REDIS_URL=redis://localhost:6379/0

# Cryptographic Secrets (Generate via: python -c "import secrets; print(secrets.token_hex(64))")
GPA_SECRET_KEY=dev_secret_jwt_key_replace_me
GPA_PEPPER=dev_pepper_hash_key_replace_me
GPA_MASTER_KEY=dev_master_aes_key_replace_me

# Environment Settings
GPA_ENV=development
FRONTEND_URL=http://localhost:5173
```

### Running the Server
```bash
uvicorn app.main:app --reload --port 8000
```
*The API will be available at `http://localhost:8000`. Interactive documentation is available at `/docs` (only in `development` mode).*

---

## 3. Frontend Configuration

The frontend is a React SPA built with Vite.

### Installation
```bash
# Open a new terminal and navigate to the frontend directory
cd frontend
npm install
```

### Environment Variables
Create a `.env` file inside the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
```

### Running the Application
```bash
npm run dev
```
*The application UI will be available at `http://localhost:5173`.*

---

## 4. Verification Workflow

To ensure your local setup is functioning correctly:
1. Open `http://localhost:5173` in your browser.
2. Register a new user account (select 3 images, click 6 points).
3. Switch to the Login tab and authenticate with the same credentials.
4. Check your backend terminal output to observe the cryptographic pipeline, challenge consumption, and biometric scoring logs.

## Troubleshooting
- **CORS Errors:** Ensure the `FRONTEND_URL` in `backend/.env` exactly matches your Vite dev server URL (no trailing slash).
- **Redis Warnings:** If you see Redis connection errors in the backend logs, it means it is falling back to in-memory state. This is fine for single-worker local development, but Redis is strictly required for multi-worker production deployments.
