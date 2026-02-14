import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import AuditLog


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _compute_hash(entry_data: str, previous_hash: str = "") -> str:
        """SHA3-256 hash chain: H(entry || prev_hash)"""
        payload = (entry_data + previous_hash).encode("utf-8")
        return hashlib.sha3_256(payload).hexdigest()

    async def _get_last_hash(self) -> str:
        """Fetch the entry_hash of the most recent audit log."""
        result = await self.db.execute(
            select(AuditLog.entry_hash)
            .order_by(desc(AuditLog.timestamp))
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row or ""

    async def create_log(
        self,
        user_id: str,
        action: str,
        ip: str,
        details: dict = None,
        risk_score: float = 0.0,
        device_hash: str = "",
    ):
        previous_hash = await self._get_last_hash()

        
        entry_data = json.dumps({
            "user_id": user_id,
            "action": action,
            "ip": ip,
            "risk_score": risk_score,
            "device_hash": device_hash,
            "details": details,
            "ts": datetime.now(timezone.utc).isoformat(),
        }, sort_keys=True)

        entry_hash = self._compute_hash(entry_data, previous_hash)

        log = AuditLog(
            user_id=user_id,
            action=action,
            ip=ip,
            details=json.dumps(details) if details else None,
            risk_score=risk_score,
            device_hash=device_hash,
            previous_hash=previous_hash or None,
            entry_hash=entry_hash,
        )
        self.db.add(log)
        await self.db.commit()
        return log

    async def verify_chain_integrity(self) -> bool:
        """Walk the entire audit chain and verify no tampering."""
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.timestamp)
        )
        logs = result.scalars().all()

        prev_hash = ""
        for log in logs:
            if log.previous_hash != (prev_hash or None):
                return False
            prev_hash = log.entry_hash
        return True
