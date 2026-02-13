"""
GPA Security Benchmarking Harness

Tests:
1. Argon2id hash time (target: <150ms)
2. SHA3-256 prehash time
3. AES-256-GCM encrypt/decrypt round-trip
4. Full auth pipeline (target: <200ms)
5. Grid-index canonicalization throughput

Run: python -m benchmark.performance_test
"""

import time
import os
import sys
import statistics

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hashlib import sha3_256
from argon2 import PasswordHasher

# ── Config ─────────────────────────────────────────────────────────────────

ITERATIONS = 10
PEPPER = "benchmark-pepper-value"

ph = PasswordHasher(
    memory_cost=65536,  # 64MB
    time_cost=2,
    parallelism=2,
    hash_len=32,
)

SAMPLE_POINTS = [
    (0.2, 0.3), (0.5, 0.5), (0.8, 0.2),
    (0.1, 0.8), (0.7, 0.7), (0.4, 0.1),
]


# ── Grid Index ─────────────────────────────────────────────────────────────

def grid_index(nx: float, ny: float) -> int:
    x_pixel = nx * 1920
    y_pixel = ny * 1080
    gx = min(int(x_pixel / 20), 95)
    gy = min(int(y_pixel / 20), 53)
    return gy * 96 + gx


def canonicalize(points):
    return "|".join(str(grid_index(x, y)) for x, y in points)


# ── Benchmarks ─────────────────────────────────────────────────────────────

def benchmark_canonicalization():
    """Benchmark grid-index canonicalization."""
    times = []
    for _ in range(ITERATIONS * 100):
        start = time.perf_counter()
        canonicalize(SAMPLE_POINTS)
        times.append((time.perf_counter() - start) * 1_000_000)  # microseconds

    avg = statistics.mean(times)
    print(f"  Canonicalization:    {avg:.1f} µs avg ({ITERATIONS * 100} runs)")
    return avg


def benchmark_sha3():
    """Benchmark SHA3-256 prehash."""
    salt = os.urandom(16)
    canonical = canonicalize(SAMPLE_POINTS)
    times = []

    for _ in range(ITERATIONS * 10):
        start = time.perf_counter()
        sha3_256(canonical.encode() + salt).digest()
        times.append((time.perf_counter() - start) * 1_000_000)

    avg = statistics.mean(times)
    print(f"  SHA3-256 prehash:    {avg:.1f} µs avg ({ITERATIONS * 10} runs)")
    return avg


def benchmark_argon2():
    """Benchmark Argon2id hashing (target: <150ms)."""
    salt = os.urandom(16)
    canonical = canonicalize(SAMPLE_POINTS)
    prehash = sha3_256(canonical.encode() + salt).digest()
    material = prehash + PEPPER.encode()
    times = []

    for _ in range(ITERATIONS):
        start = time.perf_counter()
        ph.hash(material)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    avg = statistics.mean(times)
    status = "✓ PASS" if avg < 150 else "✗ FAIL"
    print(f"  Argon2id hash:       {avg:.1f} ms avg ({ITERATIONS} runs) [{status} < 150ms]")
    return avg


def benchmark_aes_gcm():
    """Benchmark AES-256-GCM encrypt/decrypt round-trip."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import json

    key = sha3_256(b"benchmark-key").digest()
    aesgcm = AESGCM(key)
    data = json.dumps(["img_01", "img_05", "img_12"]).encode()
    times = []

    for _ in range(ITERATIONS * 10):
        start = time.perf_counter()
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, data, None)
        aesgcm.decrypt(nonce, ct, None)
        times.append((time.perf_counter() - start) * 1_000_000)

    avg = statistics.mean(times)
    print(f"  AES-256-GCM round:   {avg:.1f} µs avg ({ITERATIONS * 10} runs)")
    return avg


def benchmark_full_pipeline():
    """Benchmark full auth pipeline: canonical → SHA3 → Argon2id (target: <200ms)."""
    salt = os.urandom(16)
    times = []

    for _ in range(ITERATIONS):
        start = time.perf_counter()

        # 1. Canonicalize
        canonical = canonicalize(SAMPLE_POINTS)

        # 2. SHA3 prehash
        prehash = sha3_256(canonical.encode() + salt).digest()

        # 3. Argon2id
        ph.hash(prehash + PEPPER.encode())

        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    avg = statistics.mean(times)
    status = "✓ PASS" if avg < 200 else "✗ FAIL"
    print(f"  Full pipeline:       {avg:.1f} ms avg ({ITERATIONS} runs) [{status} < 200ms]")
    return avg


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  GPA Security Benchmark Suite")
    print("=" * 60)
    print()

    print("[1/5] Grid-Index Canonicalization")
    benchmark_canonicalization()
    print()

    print("[2/5] SHA3-256 Prehash")
    benchmark_sha3()
    print()

    print("[3/5] Argon2id Hashing (target: <150ms)")
    benchmark_argon2()
    print()

    print("[4/5] AES-256-GCM Round-Trip")
    benchmark_aes_gcm()
    print()

    print("[5/5] Full Auth Pipeline (target: <200ms)")
    benchmark_full_pipeline()
    print()

    print("=" * 60)
    print("  Benchmark complete.")
    print("=" * 60)
