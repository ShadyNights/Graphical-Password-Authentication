import time
import json
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import User, AuditLog
from app.schemas.auth_schema import LoginRequest, AuthResponse
from app.security import (
    validate_challenge, check_rate_limit, is_account_locked, should_lock_account,
    get_lockout_time, get_escalation_delay, generate_fake_hash,
    verify_gpa_secret, create_jwt_token, audit_log, get_gpa_debug_info
)
from app.biometric.rule_engine import analyze_behavioral_biometrics
from app.biometric.feature_extractor import extract_feature_vector
from app.biometric.risk_engine import risk_engine
from hashlib import sha256
from datetime import datetime


async def enforce_constant_time_helper(start_time: float, extra_delay: float = 0.0):
    from app.config import settings
    import asyncio
    elapsed_ms = (time.time() - start_time) * 1000
    target_ms = settings.CONSTANT_RESPONSE_MS + (extra_delay * 1000)
    if elapsed_ms < target_ms:
        await asyncio.sleep((target_ms - elapsed_ms) / 1000)

router = APIRouter()

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    extra_delay = 0.0

    if not check_rate_limit(client_ip):
        audit_log("login_rate_limited", username=req.username, client_ip=client_ip)
        await enforce_constant_time_helper(start_time)
        return AuthResponse(status="processing", message="Authentication result pending")

    challenge = validate_challenge(req.challenge_id, req.username)
    if not challenge:
        generate_fake_hash()
        audit_log("login_invalid_challenge", username=req.username, client_ip=client_ip)
        await enforce_constant_time_helper(start_time)
        return AuthResponse(status="processing", message="Authentication result pending")

    
    metrics = req.mouse_metrics or {}
    if req.device_fingerprint:
        metrics["device_fingerprint"] = req.device_fingerprint
        metrics["_username"] = req.username

    biometrics_result = analyze_behavioral_biometrics(metrics)
    risk_score = biometrics_result["risk_score"]
    risk_level = biometrics_result["risk_level"]

    
    ml_result = {"ml_score": 0.0, "ml_risk_level": "unknown", "ml_available": False}
    if metrics:
        features = extract_feature_vector(metrics)
        ml_result = risk_engine.compute_risk(req.username, features)
        
        
        if ml_result["ml_available"] and ml_result["ml_risk_level"] == "bot_likely":
            risk_score = max(risk_score, 0.7)
            risk_level = "bot_likely"
            biometrics_result["is_bot"] = True
            biometrics_result["reasons"].append("ml_anomaly_detected")

        
        drift_score = ml_result.get("drift_score", 0.0)
        if drift_score > 3.0:
             risk_score = max(risk_score, 0.5)
             biometrics_result["reasons"].append(f"behavioral_drift_z{drift_score}")
             if risk_level == "normal":
                 risk_level = "suspicious"

    extra_delay = get_escalation_delay(risk_score)

    if biometrics_result["is_bot"]:
        generate_fake_hash()
        audit_log(
            "login_bot_detected",
            username=req.username,
            client_ip=client_ip,
            risk_score=risk_score,
            device_fingerprint=req.device_fingerprint or "",
            details={
                "reasons": biometrics_result["reasons"],
                "component_scores": biometrics_result["component_scores"],
            }
        )
        await enforce_constant_time_helper(start_time, extra_delay)
        return AuthResponse(
            status="processing",
            message="Authentication result pending",
            risk_level=risk_level,
        )

    import traceback
    try:
        
        result = await db.execute(select(User).where(User.username == req.username))
        user = result.scalar_one_or_none()

        if not user:
            generate_fake_hash()
            audit_log("login_user_not_found", username=req.username, client_ip=client_ip, risk_score=risk_score)
            await enforce_constant_time_helper(start_time, extra_delay)
            return AuthResponse(status="processing", message="Authentication result pending")

        if is_account_locked(user):
            generate_fake_hash()
            audit_log("login_account_locked", username=req.username, client_ip=client_ip, risk_score=risk_score)
            await enforce_constant_time_helper(start_time, extra_delay)
            return AuthResponse(status="processing", message="Authentication result pending")

        
        points = [(p.x, p.y) for p in req.click_points]
        
        
        
        
        gpa_hash_str = user.gpa_hash
        if isinstance(gpa_hash_str, bytes):
             gpa_hash_str = gpa_hash_str.decode("utf-8")

        is_valid = verify_gpa_secret(
            gpa_hash_str,
            req.selected_image_ids,
            points,
            user.salt,
        )

        if is_valid:
            user.failed_attempts = 0
            user.lockout_until = None
            await db.commit()
            token = create_jwt_token(user.id, user.username)

            audit_log("login_success", username=req.username, client_ip=client_ip, risk_score=risk_score, device_fingerprint=req.device_fingerprint or "")
            
            
            ts = datetime.utcnow().isoformat()
            entry_data = f"{ts}{req.username}login_success{risk_score}".encode()
            entry_hash = sha256(entry_data).hexdigest()

            db_audit = AuditLog(
                user_id=user.id, username=req.username, ip=client_ip,
                device_hash=req.device_fingerprint or "",
                risk_score=risk_score, ml_score=ml_result.get("ml_score"),
                action="login_success",
                details=json.dumps(biometrics_result.get("component_scores", {})),
                entry_hash=entry_hash,
                timestamp=datetime.utcnow()
            )
            db.add(db_audit)
            await db.commit()

            if metrics and risk_score < 0.3:
                risk_engine.record_human_session(req.username, features)

            await enforce_constant_time_helper(start_time, extra_delay)
            return AuthResponse(status="success", message="Authentication successful", token=token, risk_level=risk_level)
        else:
            user.failed_attempts += 1
            if should_lock_account(user):
                user.lockout_until = get_lockout_time()
            await db.commit()

            audit_log("login_failed", username=req.username, client_ip=client_ip, risk_score=risk_score, details={"failed_attempts": user.failed_attempts})
            
            
            ts = datetime.utcnow().isoformat()
            entry_data = f"{ts}{req.username}login_failed{risk_score}".encode()
            entry_hash = sha256(entry_data).hexdigest()

            db_audit = AuditLog(
                user_id=user.id, username=req.username, ip=client_ip,
                device_hash=req.device_fingerprint or "",
                risk_score=risk_score, ml_score=ml_result.get("ml_score"),
                action="login_failed",
                details=json.dumps({"failed_attempts": user.failed_attempts}),
                entry_hash=entry_hash,
                timestamp=datetime.utcnow()
            )
            db.add(db_audit)
            await db.commit()

            await enforce_constant_time_helper(start_time, extra_delay)
            return AuthResponse(status="failed", message="Authentication failed", risk_level=risk_level)
    
    except Exception as e:
        print(f"CRITICAL LOGIN ERROR: {e}")
        traceback.print_exc()
        
        return AuthResponse(
            status="error", 
            message=f"Server Error: {str(e)}", 
            risk_level="unknown"
        )
