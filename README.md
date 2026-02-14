# 🔐 Next-Gen Graphical Password Authentication (GPA)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18+-61DAFB.svg)
![Security](https://img.shields.io/badge/security-FinTech--Grade-red.svg)
![Status](https://img.shields.io/badge/status-Production--Ready-success.svg)

A production-grade, adversarial-resistant graphical authentication system designed to replace traditional passwords with a high-entropy, user-centric authentication experience.

Built for high-security environments (FinTech, Defense, Enterprise SaaS) with a **Sleek-Industrial Cyber** interface and zero-trust backend architecture.

---

## 🎯 Why GPA?

Traditional passwords fail due to:
- Credential stuffing  
- Dictionary attacks  
- Reuse across services  
- Phishing exploitation  

This system replaces text-based credentials with a **hybrid graphical authentication protocol** combining recognition and cued recall mechanisms, protected by memory-hard hashing and layered abuse detection.

---

# 🛡️ Core Security Architecture

### 🔐 Hybrid Graphical Authentication
- **Recognition Layer** — Image selection from decoy grid
- **Cued Recall Layer** — Ordered click-points on secured canvas
- Combined entropy ≈ **82 bits** (comparable to 14-character random password)

---

### 🧠 Cryptographic Protections
- **Argon2id** memory-hard hashing (salted + peppered)
- **SHA-3 prehash normalization**
- **AES-256-GCM** encrypted recognition storage
- **JWT session rotation with device binding**
- **Constant-time response handling**
- **Redis distributed rate limiting**

---

### 🚨 Adversarial Defense
- Anti-enumeration responses
- Replay-resistant challenge protocol
- Automated bot detection hooks
- Lockout + adaptive delay strategy
- Secure session isolation

---

# 🎨 Next-Gen UI System

- Cyber-Industrial aesthetic
- Glassmorphism layers
- Neon state indicators
- Animated secure handshake loader
- Touch-optimized (48px targets)
- WCAG 2.1 AA compliant
- Fully keyboard accessible

---

# 🏗 Architecture Overview

> **Deep Dive:** See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed state machine and cryptographic flow.

```
User
  ↓
Frontend (Vercel)
  ↓ HTTPS
Backend (Render - FastAPI)
  ↓
PostgreSQL (Render)
  ↓
Redis (Rate Limit + Sessions)
```

---

# 🛠 Technology Stack

## Backend (FastAPI)

- Python 3.11+
- FastAPI (Async)
- SQLAlchemy Async
- PostgreSQL (Production)
- Redis (Control Plane)
- Argon2-cffi
- PyJWT
- Cryptography (AES-GCM)
- Gunicorn + Uvicorn workers

---

## Frontend (React + Vite)

- React 18
- TypeScript
- CSS Design Tokens
- Glassmorphism UI System
- Context API
- Vite build pipeline

---

# ⚡ Quick Start (Development)

## Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (optional for dev, required for prod)

---

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/gpa-secure-auth.git
cd gpa-secure-auth
```

---

## 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 4️⃣ Environment Configuration

Create `.env` inside `backend/`:

```
DATABASE_URL=
REDIS_URL=
GPA_SECRET_KEY=
GPA_PEPPER=
GPA_ENV=development
FRONTEND_URL=http://localhost:5173
```

---

# 🚢 Production Deployment

## 🌐 Cloud Architecture

| Layer | Platform |
|-------|----------|
| Frontend | Vercel |
| Backend | Render |
| Database | Render PostgreSQL |
| Redis | Render Redis |

---

## Backend (Render)

Build Command:
```
pip install -r requirements.txt
```

Start Command:
```
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --workers 4
```

Set Environment Variables in Render Dashboard.

---

## Frontend (Vercel)

Set Environment Variable:

```
VITE_API_URL=https://your-backend.onrender.com
```

Deploy via GitHub integration.

---

# 🔬 Security Model Summary

| Threat | Mitigation |
|--------|------------|
| Credential stuffing | No text passwords |
| Dictionary attack | High-entropy click permutations |
| Timing attacks | Constant-time handling |
| DB breach | Argon2id + Salt + Pepper |
| Replay attack | Nonce-based challenge |
| Automation bots | Behavioral hooks + rate limiting |

---

# 📊 Entropy Overview

Grid Positions: 5184  
Ordered Clicks: 6  
Recognition Combinations: 220  

Total Estimated Entropy:

≈ **81–82 bits**

Equivalent to:
- 14-character random alphanumeric password

---

# 🧪 Testing

Run backend tests:

```bash
pytest
```

Frontend:

```bash
npm run build
```

---

# 🤝 Contributing

1. Fork the repository  
2. Create feature branch  
3. Commit clean, documented changes  
4. Open pull request  

Security-sensitive changes must include threat-impact notes.

---

# 📄 License

MIT License — see `LICENSE`.

---

# 🧭 Roadmap

- [ ] Post-Quantum Signature Upgrade
- [ ] Multi-Region Active-Active Deployment
- [ ] Advanced Behavioral Biometrics Module
- [ ] SOC Monitoring Dashboard
- [ ] Confidential Computing Integration

---

### ⚠ Security Notice

This project is designed for research and production-grade deployment.  
If you identify a vulnerability, please report responsibly.

---

**Built for a passwordless, adversarial-resistant future.**
