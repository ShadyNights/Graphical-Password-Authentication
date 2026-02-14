import time
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from app.config import settings
from app.security.audit import audit_log


_rate_limits: defaultdict = defaultdict(list)


def check_rate_limit(client_ip: str) -> bool:
    """Returns True if request is allowed, False if rate limited."""
    now = time.time()
    window = settings.RATE_LIMIT_WINDOW_SECONDS

    _rate_limits[client_ip] = [
        ts for ts in _rate_limits[client_ip] if now - ts < window
    ]

    if len(_rate_limits[client_ip]) >= settings.RATE_LIMIT_MAX_REQUESTS:
        audit_log("rate_limit_hit", client_ip=client_ip)
        return False

    _rate_limits[client_ip].append(now)
    return True


def get_escalation_delay(risk_score: float) -> float:
    """Calculate exponential delay in seconds based on risk score."""
    if risk_score < 0.3:
        return 0.0
    elif risk_score < 0.6:
        return 1.0 + (risk_score - 0.3) * 10  
    else:
        return 3.0 + (risk_score - 0.6) * 15  


def is_account_locked(user) -> bool:
    """Check if an account is currently locked out."""
    if user.lockout_until is None:
        return False
    if user.lockout_until.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
        return True
    return False


def should_lock_account(user) -> bool:
    """Check if account should be locked based on failed attempts."""
    return user.failed_attempts >= settings.MAX_FAILED_ATTEMPTS


def get_lockout_time() -> datetime:
    """Get the lockout expiry timestamp."""
    return datetime.now(timezone.utc) + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
