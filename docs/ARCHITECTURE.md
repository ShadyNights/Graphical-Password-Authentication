# 🏗️ System Architecture & Cryptographic Flow

This document details the exact architectural flow and cryptographic pipeline implemented in the Graphical Password Authentication (GPA) system.

## 1. Registration Flow (Secret Generation)

### Phase 1: Challenge Initiation
1. **Request:** Frontend sends `POST /api/auth/challenge` with the user's identifier.
2. **Nonce Generation:** Backend generates a cryptographically secure 32-byte challenge ID (`secrets.token_urlsafe`).
3. **Grid Selection:** Backend selects a random pool of 12 images from the master catalog.
4. **State Storage:** The challenge and image pool are stored in Redis with a 300-second TTL.

### Phase 2: User Interaction
1. **Recognition:** User selects exactly 3 images from the 12-image grid.
2. **Recall:** User clicks exactly 6 ordered points on the canvas. 
3. **Submission:** Frontend normalizes coordinates to `[0.0, 1.0]` and submits the payload.

### Phase 3: Cryptographic Pipeline (Backend)
1. **Challenge Consumption:** The 300s nonce is validated and immediately deleted to prevent replay attacks.
2. **Quantization:** The normalized `[0,1]` coordinates are mapped to a 4x4 virtual grid using a strict `0.30` tolerance, producing cell indices `[0-15]`.
3. **Canonicalization:**
   - Image IDs are sorted and comma-separated (e.g., `img_01,img_04,img_12`).
   - Grid indices are pipe-separated (e.g., `4|11|2|15|9|0`).
   - The two strings are concatenated.
4. **Salting & Pre-hashing:**
   - A random 16-byte salt is generated.
   - `prehash = SHA3_256(canonical_string + salt)`
5. **Final Key Derivation:**
   - The environment `GPA_PEPPER` is appended to the pre-hash.
   - `final_hash = Argon2id(prehash + pepper)` (Configured for 64MB memory, 2 iterations, 2 parallelism).
6. **Encryption at Rest:** The raw image selections are encrypted using AES-256-GCM (keyed via `GPA_MASTER_KEY`) and stored as a `recognition_blob`.
7. **Storage:** The `identifier`, `final_hash`, `salt`, and `recognition_blob` are committed to PostgreSQL.

---

## 2. Authentication Flow (Login)

### Phase 1: Challenge Initiation
Identical to the registration flow. A fresh 300s nonce and randomized 12-image grid are generated.

### Phase 2: Interaction & Biometrics
The user selects 3 images and clicks 6 points. Simultaneously, the frontend `BiometricsCollector` passively records:
- Mouse velocity and acceleration.
- Click interval entropy.
- Interactions with invisible "honey pixel" trap coordinates.

### Phase 3: Verification & ML Scoring (Backend)
1. **Challenge Consumption & Rate Limiting:** Nonce is validated. Sliding-window rate limits (20 req / 10 min) are enforced.
2. **Behavioral Analysis:**
   - **Rule Engine:** Analyzes velocity variance, click entropy, and honey pixel hits.
   - **Risk Engine (ML):** Feature vector passed to the Scikit-learn `IsolationForest` model.
   - **Drift Detection:** Compares current behavior against the user's historical Welford Z-scores.
   - *If flagged as a bot:* The system immediately shifts to generating a fake hash to stall the attacker.
3. **Database Lookup:** The user record is retrieved. If not found, anti-enumeration fake-hashing engages.
4. **Cryptographic Verification:**
   - The submitted payload is quantized, canonicalized, and SHA3-prehashed using the *stored salt*.
   - `Argon2id.verify()` checks the resulting material against the stored database hash.
5. **Session Issuance:** On success, a 15-minute JWT is issued, and a tamper-evident event is appended to the `AuditLog`.
6. **Constant-Time Padding:** Regardless of success, failure, or bot detection, the `TimingGuardMiddleware` delays the HTTP response to ensure a minimum processing time of ~180ms.

---

## 3. Security Model Guarantees

| Threat Vector | Mitigation Strategy |
|---------------|---------------------|
| **Credential Stuffing** | Text passwords do not exist. Attacks cannot be ported from other breaches. |
| **Offline Cracking** | Server-side pepper + Argon2id memory hardness mathematically prevents GPU brute-forcing if the database leaks. |
| **Replay Attacks** | Redis enforces strict one-time consumption of challenge nonces. |
| **User Enumeration** | Timing guards and fake-hash computations ensure identical response profiles for valid and invalid usernames. |
| **Automated Botnets** | Continuous passive biometric evaluation and Isolation Forest anomaly detection. |
