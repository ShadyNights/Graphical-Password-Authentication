import math
from typing import List


def _variance(values: List[float]) -> float:
    if not values or len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


def _std_dev(values: List[float]) -> float:
    return math.sqrt(_variance(values))


def _entropy(values: List[float]) -> float:
    if not values or len(values) < 2:
        return 0.0
    min_v, max_v = min(values), max(values)
    if max_v == min_v:
        return 0.0
    num_bins = min(10, len(values))
    bin_width = (max_v - min_v) / num_bins
    counts = [0] * num_bins
    for v in values:
        idx = min(int((v - min_v) / bin_width), num_bins - 1)
        counts[idx] += 1
    total = len(values)
    entropy = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            entropy -= p * math.log2(p)
    return entropy


def _curvature_score(mouse_path: List[dict]) -> float:
    if not mouse_path or len(mouse_path) < 3:
        return 0.5
    total = 0.0
    segs = 0
    for i in range(1, len(mouse_path) - 1):
        p0, p1, p2 = mouse_path[i - 1], mouse_path[i], mouse_path[i + 1]
        v1x = p1.get("x", 0) - p0.get("x", 0)
        v1y = p1.get("y", 0) - p0.get("y", 0)
        v2x = p2.get("x", 0) - p1.get("x", 0)
        v2y = p2.get("y", 0) - p1.get("y", 0)
        cross = abs(v1x * v2y - v1y * v2x)
        m1 = math.sqrt(v1x ** 2 + v1y ** 2)
        m2 = math.sqrt(v2x ** 2 + v2y ** 2)
        if m1 > 0.001 and m2 > 0.001:
            total += cross / (m1 * m2)
            segs += 1
    if segs == 0:
        return 0.5
    avg = total / segs
    return min(max(0.0, 1.0 - avg * 5), 1.0)


def extract_feature_vector(metrics: dict) -> List[float]:
    """
    Extract the 6-dimensional feature vector from raw biometrics.
    Returns: [velocity_variance, acceleration_std, click_entropy,
              curvature_score, initial_delay_ms, jitter_score]
    """
    velocities = metrics.get("velocities", [])
    accelerations = metrics.get("accelerations", [])
    intervals = metrics.get("click_intervals", [])
    mouse_path = metrics.get("mouse_path", [])
    dwell_ms = metrics.get("dwell_time_ms", 0)
    scroll_jitter = metrics.get("scroll_jitter_count", 0)
    total_time = metrics.get("total_time_ms", 1)

    return [
        _variance(velocities),           
        _std_dev(accelerations),          
        _entropy(intervals),             
        _curvature_score(mouse_path),    
        float(dwell_ms),                 
        float(scroll_jitter) / max(total_time / 1000, 0.1),  
    ]
