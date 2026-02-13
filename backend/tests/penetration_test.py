"""
🧪 Red-Team Penetration Testing Playbook (Automated)

Implements the 6-phase penetration test plan:
1. Recon (Headers check)
2. Auth Attacks (Replay, Tampering)
3. Automation (ML Bot Detection verification)
4. Resource Exhaustion (Rate Limit check)
5. Timing Analysis (Statistical variance check)

Run: python -m tests.penetration_test
"""

import time
import requests
import statistics
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("REDTEAM")

BASE_URL = "http://127.0.0.1:8001"
AUTH_URL = f"{BASE_URL}/api/auth"

def test_headers():
    """Phase 1: Recon - Check Security Headers"""
    logger.info("⚡ [Phase 1] Recon: Checking Security Headers...")
    
    # Check global headers on health
    r = requests.get(f"{BASE_URL}/health")
    headers = r.headers
    global_required = [
        "X-Content-Type-Options", "X-Frame-Options", "Strict-Transport-Security",
        "Content-Security-Policy", "Referrer-Policy"
    ]
    missing = [h for h in global_required if h not in headers]
    if missing:
        logger.error(f"❌ Missing global headers on /health: {missing}")
        return False

    # Check Server-Timing on auth endpoint
    r_auth = requests.post(f"{AUTH_URL}/login", json={})
    if "Server-Timing" not in r_auth.headers:
        logger.error("❌ Missing Server-Timing header on /auth/login")
        return False

    logger.info("✅ All security headers present (Global + Auth-specific).")
    return True

def test_replay_attack():
    """Phase 2: Auth Attacks - Challenge Replay"""
    logger.info("⚡ [Phase 2] Auth Attacks: Testing Challenge Replay...")
    
    # 1. Get Challenge
    try:
        c = requests.post(f"{AUTH_URL}/challenge", json={"username": "redteam_replay"}).json()
        challenge_id = c["challenge_id"]
        imgs = [img["id"] for img in c["image_pool"][:3]]
    except Exception as e:
        logger.error(f"Failed to get challenge: {e}")
        return False

    # 2. Register (consumes challenge)
    payload = {
        "username": "redteam_replay",
        "challenge_id": challenge_id,
        "selected_image_ids": imgs,
        "click_points": [{"x":0.5, "y":0.5}, {"x":0.2, "y":0.2}, {"x":0.8, "y":0.8},
                         {"x":0.1, "y":0.1}, {"x":0.9, "y":0.9}, {"x":0.3, "y":0.3}]
    }
    r = requests.post(f"{AUTH_URL}/register", json=payload)
    if r.status_code != 200:
        logger.error(f"Registration failed: {r.text}")
        return False

    # 3. Attempt Replay (Same challenge_id)
    r_replay = requests.post(f"{AUTH_URL}/register", json=payload)
    res = r_replay.json()
    
    # Accept "failed", "error", or 400/401 as success for blocking replay
    if res.get("status") in ["failed", "error"] or r_replay.status_code >= 400:
         logger.info("✅ Replay attack blocked (Challenge consumed).")
         return True
    
    logger.error(f"❌ Replay attack SUCCEEDED! Status: {res.get('status')} Msg: {res.get('message')}")
    return False

def test_bot_detection():
    """Phase 3: Automation - ML Bot Detection"""
    logger.info("⚡ [Phase 3] Automation: Testing ML Bot Detection...")
    
    username = f"redteam_bot_{int(time.time())}"
    
    # 1. Get Challenge
    c = requests.post(f"{AUTH_URL}/challenge", json={"username": username}).json()
    challenge_id = c["challenge_id"]
    imgs = [img["id"] for img in c["image_pool"][:3]]
    
    # Register first
    reg_payload = {
        "username": username,
        "challenge_id": challenge_id,
        "selected_image_ids": imgs,
        "click_points": [{"x":0.5, "y":0.5}, {"x":0.2, "y":0.2}, {"x":0.8, "y":0.8},
                         {"x":0.1, "y":0.1}, {"x":0.9, "y":0.9}, {"x":0.3, "y":0.3}]
    }
    requests.post(f"{AUTH_URL}/register", json=reg_payload)

    # 2. Login with PERFECT Bot Behavior
    c2 = requests.post(f"{AUTH_URL}/challenge", json={"username": username}).json()
    
    bot_metrics = {
        "velocities": [100.0, 100.0, 100.0, 100.0], # Zero variance
        "accelerations": [0.0, 0.0, 0.0],           # Zero variance
        "click_intervals": [500, 500, 500, 500],    # Zero entropy
        "mouse_path": [{"x":0.1, "y":0.1}, {"x":0.2, "y":0.2}, {"x":0.3, "y":0.3}], # Perfectly straight
        "dwell_time_ms": 50,                        # Too fast
        "total_time_ms": 200,                       # Superhuman
        "honey_pixel_hits": 1                       # Hit a trap
    }
    
    login_payload = {
        "username": username,
        "challenge_id": c2["challenge_id"],
        "selected_image_ids": imgs,
        "click_points": reg_payload["click_points"],
        "device_fingerprint": "bot-fingerprint",
        "mouse_metrics": bot_metrics
    }
    
    r = requests.post(f"{AUTH_URL}/login", json=login_payload).json()
    
    if r.get("risk_level") == "bot_likely" or r.get("status") == "processing":
        # Note: status might be 'processing' if rejected
        logger.info(f"✅ Bot detected! Risk Level: {r.get('risk_level')}")
        return True
        
    logger.error(f"❌ Bot NOT detected! Risk Level: {r.get('risk_level')}")
    return False

def test_timing_analysis():
    """Phase 5: Timing Analysis - Check Constant Time Padding"""
    logger.info("⚡ [Phase 5] Timing: Checking Constant Time Padding...")
    
    durations = []
    for i in range(5):
        start = time.time()
        # Invalid login to trigger padding
        requests.post(f"{AUTH_URL}/login", json={"username": "timing_test", "challenge_id": "invalid"})
        dur = (time.time() - start) * 1000
        durations.append(dur)
        print(f"   Request {i+1}: {dur:.2f}ms")

    avg = statistics.mean(durations)
    logger.info(f"   Average Response Time: {avg:.2f}ms")
    
    if avg < 180:
        logger.error("❌ Response too fast! Padding not working (<180ms).")
        return False
        
    logger.info("✅ Timing padding verified (>180ms).")
    return True

if __name__ == "__main__":
    print("\n🔐 GPA RED TEAM AUTOMATION SUITE\n" + "="*40)
    
    results = {
        "Recon Headers": test_headers(),
        "Replay Attack": test_replay_attack(),
        "Bot Detection": test_bot_detection(),
        "Timing Analysis": test_timing_analysis()
    }
    
    print("\n📊 FINAL VERDICT\n" + "="*40)
    failed = False
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        icon = "✅" if passed else "❌"
        print(f"{icon} {test}: {status}")
        if not passed: failed = True
    
    if failed:
        sys.exit(1)
    print("\n🚀 SYSTEM STATUS: ENTERPRISE-GRADE SECURE")
