import uuid
from datetime import datetime
from sqlalchemy import Column, String, LargeBinary, Integer, DateTime, Float, Text
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(64), unique=True, nullable=False, index=True)
    gpa_hash = Column(LargeBinary, nullable=False)
    salt = Column(LargeBinary, nullable=False)
    recognition_blob = Column(LargeBinary, nullable=False)  # AES-256-GCM encrypted image IDs
    failed_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """
    STRIDE-compliant append-only audit log.
    Provides non-repudiation for all authentication events.
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True, index=True)
    username = Column(String(64), nullable=True, index=True)
    ip = Column(String(45), nullable=True)            # IPv4/IPv6
    device_hash = Column(String(64), nullable=True)    # SHA-256 fingerprint
    risk_score = Column(Float, default=0.0)
    ml_score = Column(Float, nullable=True)            # Isolation Forest score
    action = Column(String(64), nullable=False, index=True)
    details = Column(Text, nullable=True)              # JSON extra data
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    previous_hash = Column(String(128), nullable=True)   # SHA3-256 of previous entry
    entry_hash = Column(String(128), nullable=False)      # SHA3-256(entry + previous_hash)


class Session(Base):
    """
    Active user sessions with rotation support.
    """
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    refresh_token = Column(String, unique=True, nullable=False)
    device_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
