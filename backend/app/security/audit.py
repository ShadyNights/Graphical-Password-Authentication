import logging
import json
from datetime import datetime, timezone

# ── Structured Audit Logger ────────────────────────────────────────────────

audit_logger = logging.getLogger("gpa.audit")
audit_logger.setLevel(logging.INFO)

# Ensure handler is not added multiple times during reloads
if not audit_logger.handlers:
    _handler = logging.FileHandler("audit.log")
    _handler.setFormatter(logging.Formatter(
        '{"ts":"%(asctime)s","level":"%(levelname)s","event":%(message)s}'
    ))
    audit_logger.addHandler(_handler)


def audit_log(
    event_type: str,
    username: str = "",
    client_ip: str = "",
    risk_score: float = 0.0,
    device_fingerprint: str = "",
    details: dict = None,
):
    """Write a structured audit event to the security log."""
    entry = {
        "type": event_type,
        "username": username,
        "ip": client_ip,
        "risk_score": round(risk_score, 4),
        "device_fp": device_fingerprint[:16] + "..." if len(device_fingerprint) > 16 else device_fingerprint,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if details:
        entry["details"] = details
    audit_logger.info(json.dumps(entry))
