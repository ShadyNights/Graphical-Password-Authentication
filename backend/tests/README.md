# Red Team Verification Suite

This directory contains the automated penetration testing suite for the GPA system.

## Running the Tests

Ensure the backend server is running on port **8001** (to avoid conflicts with dev servers on 8000), or update `BASE_URL` in `penetration_test.py`.

### 1. Start Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### 2. Run Tests
In a separate terminal:
```bash
python -m tests.penetration_test
```

## Test Coverage
- **Recon**: Security headers (HSTS, CSP, etc.)
- **Auth Attacks**: Challenge replay protection
- **Automation**: ML-based Bot Detection (Velocity, Entropy, Curvature)
- **Timing**: Constant-time response verification (>180ms padding)
