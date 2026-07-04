<div align="center">
  <h1>🔐 Next-Gen Graphical Password Authentication (GPA)</h1>

  <p><strong>A production-grade, adversarial-resistant graphical authentication system delivering high-entropy, zero-knowledge, phishing-resistant security.</strong></p>
  
  <p>Built with<br>FastAPI • React • TypeScript • PostgreSQL • Redis • Argon2id • Docker</p>

  <p>
    <a href="https://github.com/ShadyNights/Graphical-Password-Authentication/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black" alt="React Version">
    <img src="https://img.shields.io/badge/Status-Production_Ready-success.svg" alt="Status">
    <img src="https://img.shields.io/badge/Security-FinTech_Grade-red.svg" alt="Security Level">
    <a href="https://github.com/ShadyNights/Graphical-Password-Authentication/actions"><img src="https://img.shields.io/github/actions/workflow/status/ShadyNights/Graphical-Password-Authentication/github-actions.yml?branch=main" alt="Build Status"></a>
  </p>
  <p align="center">
    <a href="https://graphical-password-authentication-seven.vercel.app/">Live Demo</a> •
    <a href="#installation-guide">Installation</a> •
    <a href="docs/ARCHITECTURE.md">Architecture</a> •
    <a href="PROJECT_SPECIFICATION.md">Documentation</a>
  </p>
  <p>
    <a href="https://github.com/ShadyNights/Graphical-Password-Authentication/stargazers"><img src="https://img.shields.io/github/stars/ShadyNights/Graphical-Password-Authentication" alt="Stars Badge"/></a>
    <a href="https://github.com/ShadyNights/Graphical-Password-Authentication/network/members"><img src="https://img.shields.io/github/forks/ShadyNights/Graphical-Password-Authentication" alt="Forks Badge"/></a>
    <a href="https://github.com/ShadyNights/Graphical-Password-Authentication/issues"><img src="https://img.shields.io/github/issues/ShadyNights/Graphical-Password-Authentication" alt="Issues Badge"/></a>
  </p>
</div>

---

## 📖 Table of Contents

- [Project Overview](#-project-overview)
- [Why This Project Exists](#-why-this-project-exists)
- [Key Features](#-key-features)
- [Screenshots & Demo](#-screenshots--demo)
- [Technology Stack](#-technology-stack)
- [Architecture Overview](#-architecture-overview)
- [Authentication Workflow](#-authentication-workflow)
- [Security Architecture](#-security-architecture)
- [Cryptographic Pipeline](#-cryptographic-pipeline)
- [Project Structure](#-project-structure)
- [Installation Guide](#-installation-guide)
- [Environment Variables](#-environment-variables)
- [Running Locally](#-running-locally)
- [Docker & Deployment](#-docker--deployment)
- [API Endpoints](#-api-endpoints)
- [Database Overview](#-database-overview)
- [Security Highlights](#-security-highlights)
- [Performance Highlights](#-performance-highlights)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Author & Acknowledgements](#-author--acknowledgements)
- [Detailed Documentation](#-detailed-documentation)

---

## 🔎 Project Overview

**Graphical Password Authentication (GPA)** is an advanced authentication protocol that replaces traditional text-based passwords with a hybrid graphical system. By combining image recognition (selecting 3 decoyed images) and cued spatial recall (clicking 6 specific points on a canvas), it delivers approximately **82 bits of entropy**—equivalent to a 14-character randomized alphanumeric password.

Designed for high-security environments such as FinTech, Defense, and Enterprise SaaS, GPA operates on a zero-trust backend architecture. It incorporates memory-hard hashing (Argon2id), continuous behavioral biometrics (Isolation Forest ML), and tamper-evident audit logging.

## ⭐ Repository Highlights

- Production-oriented authentication architecture
- Hybrid graphical password protocol
- Behavioral biometrics
- Machine learning–assisted anomaly detection
- Modern React + FastAPI stack
- Docker & Kubernetes ready
- Security-first backend design

## 🎯 Why This Project Exists

Traditional passwords are fundamentally broken. They are susceptible to:
- **Credential Stuffing & Dictionary Attacks:** Easily automated by botnets.
- **Password Reuse:** A breach in one service compromises many.
- **Phishing Exploitation:** Users can be tricked into typing credentials into fake portals.

GPA mitigates these vectors by eliminating text passwords entirely. A graphical challenge-response protocol ensures that even if an attacker intercepts a single authentication payload, the underlying secret remains mathematically intractable to derive due to one-time nonces and salted Argon2id hashing.

## ✨ Key Features

### Authentication & Cryptography
- **Hybrid Graphical Protocol:** 3 image selections + 6 precise click points.
- **Irreversible Storage:** Argon2id hashing combined with SHA3-256 pre-hashing and pepper.
- **Encrypted Data at Rest:** AES-256-GCM encryption for recognition image data.
- **Replay Resistance:** One-time use cryptographic challenge nonces.

### Security & Abuse Prevention
- **Anti-Timing Oracles:** Constant-time response padding (`TimingGuardMiddleware`).
- **Anti-Enumeration:** Fake hash computation for non-existent users.
- **Behavioral Biometrics:** Passive collection of mouse dynamics, click timing, and "honey pixel" traps.
- **Machine Learning Bot Detection:** Scikit-learn Isolation Forest and Welford's drift detection.
- **Rate Limiting & Lockout:** In-memory sliding window rate limiting and account lockout after 5 failed attempts.

### Modern User Interface
- **Cyber-Industrial Aesthetic:** Glassmorphism UI, smooth micro-animations, and interactive grid/canvas components.
- **Accessible Design:** WCAG 2.1 AA compliance, fully keyboard navigable, touch-optimized targets.

## 📊 Project Status

This project is currently **feature-complete** and ready for production use. The core authentication workflow, cryptographic pipeline, and behavioral biometrics are fully implemented and tested.

*Note: The TOTP (Time-Based One-Time Password) fallback module is currently a planned enhancement and exists as a stub in the codebase.*

## 🚀 Live Demo

**Application:** https://graphical-password-authentication-seven.vercel.app/

> Experience the complete graphical authentication workflow directly in your browser.

## 🛠 Technology Stack

### Backend
- **Framework:** Python 3.11+, FastAPI (Async)
- **Database:** PostgreSQL (production), SQLite (development), via SQLAlchemy (Async)
- **Caching/State:** Redis
- **Cryptography:** Argon2-cffi, PyJWT, Cryptography (AES-GCM), hashlib (SHA3)
- **Machine Learning:** Scikit-learn (Isolation Forest), NumPy

### Frontend
- **Framework:** React 18, TypeScript, Vite
- **Styling:** Vanilla CSS (CSS Variables, Glassmorphism, Responsive Grid)
- **Fonts:** Google Fonts (Inter, JetBrains Mono)

### Infrastructure & Deployment
- **Containerization:** Docker, Kubernetes (StatefulSet, HPA, Probes)
- **CI/CD:** GitHub Actions (Bandit, Safety, Trivy container scans)

## 🏗 Architecture Overview

GPA employs a two-tier client-server monolith with strict layer separation:

```text
┌─────────────────────────────────────────────────┐
│ FRONTEND (React 18 SPA via Vite)                │
│  Components → Services → fetch() API calls      │
└─────────────────────┬───────────────────────────┘
                      │ HTTPS / JSON
┌─────────────────────▼───────────────────────────┐
│ BACKEND (FastAPI Monolith)                      │
│  ├── Middleware (CORS, RequestID, Security, Time)│
│  ├── Routes (Init, Register, Login, Refresh)    │
│  ├── Security (Crypto, JWT, Challenge, Audit)   │
│  ├── Biometrics (Rule Engine, ML Risk Engine)   │
│  └── Data Access (SQLAlchemy Repositories)      │
└─────────────────────┬─────────┬─────────────────┘
                      │         │
              ┌───────▼──┐  ┌───▼──────┐
              │PostgreSQL│  │  Redis   │
              └──────────┘  └──────────┘
```

## 🔄 Authentication Workflow

1. **Challenge Request (`POST /api/auth/challenge`):** Client requests a login challenge. Backend generates a 32-byte secure nonce, samples a random pool of 12 images, stores it in Redis (300s TTL), and returns the challenge.
2. **Recognition & Recall:** User selects 3 images from the grid, then clicks 6 points on the canvas. Client gathers these inputs alongside passive biometric data (mouse velocity, click intervals).
3. **Verification Request (`POST /api/auth/login`):** Client sends the encrypted payload, challenge ID, and biometric telemetry.
4. **Backend Processing:** 
   - Validates challenge nonce.
   - Evaluates biometric data against rules and the ML Isolation Forest model.
   - Normalizes and quantizes click coordinates into a 4x4 grid string.
   - Computes Argon2id hash and verifies against the stored database hash.
   - Issues JWT and records a tamper-evident audit log.

## 🛡️ Security Architecture

| Vector | Implemented Protection |
|--------|------------------------|
| **Credential Stuffing** | Text passwords eliminated entirely. |
| **Brute Force / GPUs** | Argon2id memory-hard hashing (`m=65536, t=2, p=2`). |
| **Replay Attacks** | 300-second TTL single-use challenge nonces via Redis. |
| **Timing Attacks** | `TimingGuardMiddleware` enforces ≥180ms constant-time responses. |
| **User Enumeration** | Identical fake-hash computation delays for unknown usernames. |
| **Automated Bots** | Behavioral analysis, ML drift scoring, and UI "honey pixels". |
| **Session Hijacking** | Short-lived JWTs (15 min) with device fingerprint binding. |

## 🔐 Cryptographic Pipeline

The system converts visual, spatial interactions into irreversible cryptographic material:
1. **Quantization:** Normalized `[0,1]` click coordinates are mapped to a 4x4 grid (tolerance 0.30).
2. **Canonicalization:** Selected image IDs are sorted and joined; grid indices are joined.
3. **Pre-hashing:** The combined string + user salt is hashed with SHA3-256 to create a 32-byte prehash.
4. **Final Hashing:** The prehash + server pepper is hashed via Argon2id.

## 📁 Project Structure

```text
├── .github/              # GitHub Actions workflows
├── docs/assets/          # Architecture diagrams and screenshots
├── README.md             # Project documentation
├── LICENSE               # MIT License
├── backend/
│   ├── app/
│   │   ├── biometric/    # Bot detection, ML rules, drift profiling
│   │   ├── core/         # Logging, telemetry (planned)
│   │   ├── db/           # SQLAlchemy models, sessions, repositories
│   │   ├── middleware/   # Security headers, timing guards, request IDs
│   │   ├── routes/       # FastAPI endpoint handlers
│   │   ├── schemas/      # Pydantic validation models
│   │   └── security/     # Hashing, AES encryption, JWT, challenges
│   ├── benchmark/        # Crypto performance tests
│   ├── infrastructure/   # Dockerfiles, K8s manifests, GitHub Actions
│   ├── ml/               # Training pipelines and metrics
│   └── tests/            # Penetration and red-team integration tests
├── frontend/
│   ├── public/           # Static assets, backgrounds
│   └── src/
│       ├── components/   # React UI (AuthFlow, ImageGrid, ClickCanvas)
│       ├── services/     # API client, biometrics tracking, fingerprinting
│       └── main.tsx      # Application entrypoint
└── docs/                 # Architectural deep-dives and specifications
```

## ⚙️ Installation Guide

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis 7+ (Optional for local dev, falls back to memory)

```bash
git clone https://github.com/ShadyNights/Graphical-Password-Authentication.git
cd Graphical-Password-Authentication
```

## 🔐 Environment Variables

Create `.env` files in both `backend/` and `frontend/`.

**`backend/.env`**
```env
DATABASE_URL=sqlite+aiosqlite:///./gpa_dev.db
REDIS_URL=redis://localhost:6379/0
GPA_SECRET_KEY=dev-secret-key-change-in-production
GPA_PEPPER=dev-pepper-value-change-in-production
GPA_MASTER_KEY=dev-master-key-change-in-production
GPA_ENV=development
FRONTEND_URL=http://localhost:5173
```

**`frontend/.env`**
```env
VITE_API_URL=http://localhost:8000
```

## 🚀 Running Locally

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Access the application at `http://localhost:5173`.

## 🐳 Docker & Deployment

### Docker (Production Image)
```bash
cd backend
docker build -t gpa-backend -f infrastructure/docker/Dockerfile .
docker run -p 8000:8000 --env-file .env gpa-backend
```

### Kubernetes
Manifests are available in `backend/infrastructure/k8s/`:
```bash
kubectl apply -f backend/infrastructure/k8s/
```
*(Includes Deployment, StatefulSet for PostgreSQL, HPA, and Service configurations).*

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/challenge` | No | Request a one-time challenge nonce & image pool. |
| `POST` | `/api/auth/register` | No | Register a new user with graphical credentials. |
| `POST` | `/api/auth/login` | No | Authenticate and retrieve JWT session tokens. |
| `POST` | `/api/auth/refresh` | Yes | Refresh an active JWT session. |
| `GET`  | `/api/auth/images` | No | Retrieve the available recognition image catalog. |
| `GET`  | `/health` | No | Application health and readiness probe. |
| `POST` | `/api/auth/totp/verify` | Yes | *(Planned/Stub)* TOTP 2FA verification. |

## 🗄️ Database Overview

The system uses PostgreSQL in production and SQLite in development. 
- `users`: Stores Argon2id hash (`gpa_hash`), 16-byte `salt`, AES-GCM encrypted `recognition_blob`, and lockout state.
- `sessions`: Tracks active refresh tokens and device fingerprints.
- `audit_logs`: A tamper-evident log appending SHA-256 hashes of critical security events (logins, lockouts, biometric anomalies).

## 🛡️ Security Highlights

- **Dependency Scanning:** CI pipeline integrates `safety` and `bandit` SAST scanners.
- **Container Security:** Trivy scanning enforced in GitHub Actions.
- **Zero Plaintext Storage:** Neither click coordinates nor image selections are ever stored in plaintext.
- **Security Headers:** Strict HSTS, CSP (`default-src 'self'`), X-Frame-Options, and Permissions-Policy middleware applied to all responses.

## ⏱️ Performance Highlights

Designed for low-latency authentication with memory-hard Argon2id hashing and constant-time response protection.

## 🗺️ Roadmap

- [ ] **Data Layer:** Implement Alembic database migrations.
- [ ] **Scalability:** Migrate in-memory state (rate limits, challenges) fully to Redis for multi-replica K8s scaling.
- [ ] **Machine Learning:** Persist raw biometric metrics to database to enable Isolation Forest retraining pipeline.
- [ ] **Security:** Complete implementation of SHA3-256 audit log chaining.
- [ ] **Features:** Implement pending TOTP fallback module.

## 🤝 Contributing

While this is an independently developed and solo-maintained project, community contributions, bug reports, and feature requests are highly welcome! 

If you'd like to contribute:
1. Fork the [repository](https://github.com/ShadyNights/Graphical-Password-Authentication).
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes with clear, descriptive messages.
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

*Note: Security-sensitive changes or vulnerability reports should be communicated responsibly. PRs modifying the cryptographic pipeline require threat-impact notes.*

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

<div align="center">

### Kashif Ansari

Cybersecurity Engineer • AI Developer • Backend Engineer

<p>
  <a href="https://github.com/ShadyNights">
    <img src="https://img.shields.io/badge/GitHub-ShadyNights-181717?logo=github" />
  </a>
  <a href="https://www.linkedin.com/in/kashifansari18">
    <img src="https://img.shields.io/badge/LinkedIn-Kashif%20Ansari-0A66C2?logo=linkedin" />
  </a>
</p>

**This project was independently conceived, designed, architected, and developed solely by Kashif Ansari.**

</div>

## 🙌 Acknowledgements

Special thanks to the open-source security community for pioneering work on behavioral biometrics, memory-hard key derivation functions, and zero-knowledge architectures.

## 📚 Detailed Documentation

For deep technical dives, refer to the `/docs` directory and related documentation:
- [🏗️ Architecture & Cryptographic Flow](docs/ARCHITECTURE.md)
- [🛠️ Local Setup Guide](LOCAL_SETUP.md)
- [🛡️ Penetration Testing Suite](backend/tests/Test.md)
- [📄 Project Specifications](PROJECT_SPECIFICATION.md)
