# System Architecture & Authentication Flow

## 🔐 Part 1: Create Graphical Password (Registration Flow)

### UI Interaction
**Flow:** Pending → Identity → Recognition → Recall

### 🟢 Step 1: Identity Phase
**User Action:** Enters identifier (e.g., `shady@securemail.com`).

**Frontend:**
- Sends `POST /auth/init-registration` with `{ identifier }`.

**Backend:**
1. Checks if identifier exists.
2. If new, generates:
   - `registration_challenge_id` (UUID)
   - Signed nonce (HMAC-SHA256)
3. Stores challenge in Redis (`reg_challenge:{uuid}`) with 60s TTL.

### 🟢 Step 2: Recognition Phase
**UI:** Shows 4x4 image grid (16 images).
**User:** Selects 3 secret images.
**Purpose:** Adds entropy and prevents shoulder surfing.
**Data:** `selected_images: [4, 9, 12]` (Indexes).

### 🟢 Step 3: Recall Phase (Click Canvas)
**User:** Clicks 6 ordered points on the image.
**Example:** `[(100,200), (350,400), ...]` (normalized by frontend).
**Frontend:** Sends `POST /auth/register` with:
```json
{
  "identifier": "shady@securemail.com",
  "challenge_id": "uuid",
  "selected_images": ["img_04", "img_09", "img_12"],
  "click_points": [{"x": 0.1, "y": 0.2}, ...]
}
```

### 🧠 Backend Logic (Critical Security Step)
1.  **Verify Challenge:** Checks Redis, validates nonce, deletes challenge.
2.  **Canonicalize Click Points:**
    - Converts to grid index: `index = floor(x/CELL_W) + (floor(y/CELL_H) * GRID_WIDTH)`.
    - Example: `"128|490|3321|51|2990|100"`.
3.  **Generate Salt:** `salt = os.urandom(16)`.
4.  **Prehash:** `prehash = SHA3(canonical_string + salt)`.
5.  **Retrieve Pepper:** From ENV (`GPA_PEPPER`) or HSM.
6.  **Argon2id Hash:** `final_hash = Argon2id(prehash + pepper)`.
7.  **Encrypt Recognition:**
    - Encrypts `[4, 9, 12]` using AES-256-GCM (Master Key).

### 🗄 Database Storage
| Field | Value |
|-------|-------|
| `identifier` | `shady@securemail.com` |
| `gpa_hash` | Argon2id hash |
| `salt` | Random 16 bytes |
| `recognition_blob` | AES Encrypted Blob |
| `failed_attempts` | 0 |

> **Note:** No plaintext coordinates or images are ever stored.

---

## 🔐 Part 2: Authenticate Identity (Login Flow)

### 🔵 Step 1: Identity Phase
**Frontend:** `POST /auth/init-login` with `{ identifier }`.
**Backend:**
- Fetches user (generic response if not found).
- Generates login challenge.
- Shuffles recognition grid.
- Stores challenge in Redis (60s TTL).

### 🔵 Step 2: Recognition Phase
**User:** Selects the same 3 images.
**Backend:**
- Decrypts `recognition_blob` -> `[4, 9, 12]`.
- Compares with user selection.
- If mismatch -> Fail (generic response).

### 🔵 Step 3: Recall Phase
**User:** Clicks 6 points again.
**Frontend:** Sends `click_points`.

### 🧠 Backend Verification Logic
1.  **Canonicalize Clicks:** Same logic as registration.
2.  **Prehash:** `prehash = SHA3(canonical_string + stored_salt)`.
3.  **Retrieve Pepper.**
4.  **Argon2 Verify:** `Argon2.verify(stored_hash, prehash + pepper)`.

### 🔐 Step 4: Behavioral Analysis (Optional)
- Analyzes mouse velocity, click timing entropy, movement randomness.
- If suspicious: Adds delay or forces TOTP.

### 🔐 Step 5: Session Creation
- Generates `session_id`.
- Issues **JWT Access Token** (5 min) and **Refresh Token** (15 min).
- Stores session in DB and Redis.
- **UI:** Transitions to "Success" animation.

### 🔴 Failure Flow
- Increment `failed_attempts`.
- Lock account if threshold exceeded.
- Return generic "Authentication Failed" message (minimize information leakage).

---

## 🛡 Security Model

### Against Credential Stuffing
- No password field.
- No text credentials to reuse.

### Against Dictionary Attack
- Search space: `5184 P 6` ≈ **1.9 × 10^22**.
- Impossible to brute-force online.
- Rate limiting: 5 attempts per 10 min.

### Against DB Breach
- Attacker gets: Hash, Salt, Encrypted Recognition.
- **Cannot recover:** Click points, Recognition pattern (without Pepper/Master Key).

### Against Replay Attack
- Challenge nonce (One-time use, 60s expiry).

### Against Timing Attack
- Response padding (Constant ~180ms).

---

## ⚡ Mental Model
- **Recognition:** "Something you recognize" (Images).
- **Recall:** "Something you remember spatially" (Clicks).
- **Argon2:** "Impossible to crack" (Storage).
- **Redis:** "Traffic control" (State/Rate limit).
- **JWT:** "Temporary identity passport" (Session).
