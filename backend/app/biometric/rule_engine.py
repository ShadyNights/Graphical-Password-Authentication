from typing import Optional
from app.biometric.feature_extractor import _variance, _entropy, _curvature_score
from app.security.audit import audit_log


from collections import defaultdict
_device_history: defaultdict = defaultdict(list)


def validate_device_fingerprint(username: str, fingerprint_hash: str) -> str:
    """
    Validate device fingerprint against user history.
    Returns: 'known', 'new_device', or 'anomalous'
    """
    history = _device_history.get(username, [])

    if not history:
        _device_history[username].append(fingerprint_hash)
        return "new_device"

    if fingerprint_hash in history:
        return "known"

    
    if len(history) < 5:
        _device_history[username].append(fingerprint_hash)
        return "new_device"

    
    audit_log("device_anomaly", username=username, device_fingerprint=fingerprint_hash,
              details={"known_devices": len(history)})
    return "anomalous"


def analyze_behavioral_biometrics(metrics: Optional[dict]) -> dict:
    """
    Advanced behavioral biometrics analysis using Phase II weighted risk scoring.
    """
    if not metrics:
        return {
            "risk_score": 0.2,
            "risk_level": "unknown",
            "is_bot": False,
            "reasons": ["no_metrics_provided"],
            "component_scores": {},
        }

    reasons = []
    component_scores = {}

    
    velocity_score = 0.0
    velocities = metrics.get("velocities", [])
    if velocities and len(velocities) > 2:
        variance = _variance(velocities)
        if variance < 0.001:
            velocity_score = 1.0
            reasons.append("uniform_mouse_velocity")
        elif variance < 0.01:
            velocity_score = 0.6
            reasons.append("low_velocity_variance")
        else:
            velocity_score = max(0.0, 0.3 - variance * 2)

        accelerations = metrics.get("accelerations", [])
        if accelerations and len(accelerations) > 2:
            accel_var = _variance(accelerations)
            if accel_var < 0.0005:
                velocity_score = min(1.0, velocity_score + 0.3)
                reasons.append("uniform_acceleration")
    else:
        velocity_score = 0.3

    component_scores["velocity_variance"] = round(velocity_score, 4)

    
    entropy_score = 0.0
    intervals = metrics.get("click_intervals", [])
    if intervals and len(intervals) > 2:
        entropy = _entropy(intervals)
        if entropy < 0.5:
            entropy_score = 1.0
            reasons.append("extremely_low_click_entropy")
        elif entropy < 1.5:
            entropy_score = 0.6
            reasons.append("low_click_entropy")
        elif entropy > 2.5:
            entropy_score = 0.0
        else:
            entropy_score = max(0.0, (2.5 - entropy) / 2.0)
    else:
        entropy_score = 0.2

    component_scores["click_entropy"] = round(entropy_score, 4)

    
    mouse_path = metrics.get("mouse_path", [])
    curvature_score = _curvature_score(mouse_path)
    if curvature_score > 0.8:
        reasons.append("straight_line_movement")
    elif curvature_score > 0.6:
        reasons.append("low_path_curvature")

    component_scores["curvature"] = round(curvature_score, 4)

    
    device_score = 0.0
    dwell_time = metrics.get("dwell_time_ms", 0)
    if 0 < dwell_time < 100:
        device_score += 0.3
        reasons.append("instant_first_click")

    total_time = metrics.get("total_time_ms", 0)
    if 0 < total_time < 500:
        device_score += 0.3
        reasons.append("impossibly_fast_interaction")

    honey_hits = metrics.get("honey_pixel_hits", 0)
    if honey_hits > 0:
        device_score += 0.4
        reasons.append(f"honey_pixel_{honey_hits}x")

    scroll_events = metrics.get("scroll_jitter_count", 0)
    if total_time > 2000 and scroll_events == 0:
        device_score += 0.1
        reasons.append("no_scroll_jitter")

    device_fp = metrics.get("device_fingerprint", "")
    username = metrics.get("_username", "")
    if device_fp and username:
        fp_result = validate_device_fingerprint(username, device_fp)
        if fp_result == "new_device":
            device_score += 0.1
            reasons.append("new_device")
        elif fp_result == "anomalous":
            device_score += 0.2
            reasons.append("device_anomaly")

    device_score = min(device_score, 1.0)
    component_scores["device_anomaly"] = round(device_score, 4)

    
    risk_score = (
        0.3 * velocity_score +
        0.2 * entropy_score +
        0.2 * curvature_score +
        0.3 * device_score
    )
    risk_score = min(risk_score, 1.0)

    
    if risk_score < 0.3:
        risk_level = "normal"
    elif risk_score < 0.6:
        risk_level = "suspicious"
    else:
        risk_level = "bot_likely"

    return {
        "risk_score": round(risk_score, 4),
        "risk_level": risk_level,
        "is_bot": risk_score >= 0.6,
        "reasons": reasons,
        "component_scores": component_scores,
    }
