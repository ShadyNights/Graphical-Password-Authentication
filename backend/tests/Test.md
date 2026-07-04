# 🛡️ Penetration & Security Testing Suite

This directory contains the automated adversarial testing suite for the Graphical Password Authentication (GPA) system. It is designed to validate the security posture against common attack vectors.

## Overview

The test suite (`penetration_test.py`) acts as an automated red-team agent, communicating over HTTP to verify that the cryptographic, behavioral, and rate-limiting defenses function correctly under attack conditions.

## Test Coverage

1. **Reconnaissance & Header Analysis**
   - Verifies strict enforcement of HSTS, Content-Security-Policy (CSP), X-Frame-Options, and anti-sniffing headers.
2. **Replay Attack Prevention**
   - Attempts to reuse a previously valid challenge nonce.
   - Validates that challenges are consumed immediately and rejected on subsequent attempts.
3. **Behavioral Bot Detection**
   - Simulates superhuman interaction speeds and mathematically perfect straight-line cursor movements.
   - Verifies that the ML/rules engine flags the interaction and enforces adaptive delays or rejects the request.
4. **Timing Oracle Resistance**
   - Analyzes response times across valid, invalid, and non-existent users.
   - Verifies that the `TimingGuardMiddleware` enforces a strict lower bound on response times (default ~180ms), preventing side-channel user enumeration.

## Execution Guide

### 1. Start the Target Environment
Ensure the backend server is running in a controlled testing environment (not production). By default, the tests expect the server on port `8001` to avoid conflicting with development servers.

```bash
# In the backend directory
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### 2. Launch the Suite
In a separate terminal, execute the penetration tests:

```bash
# In the backend directory
python -m tests.penetration_test
```

### Troubleshooting
- **Connection Refused:** Ensure the `BASE_URL` in `penetration_test.py` matches your running server.
- **Missing Dependencies:** The suite requires the `requests` library. Ensure your virtual environment is active.
