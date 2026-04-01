"""
Verification utilities for email and SMS.
"""
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.cache import get_redis


def generate_verification_code(length: int = 6) -> str:
    """Generate a random verification code."""
    return ''.join(random.choices(string.digits, k=length))


def store_verification_code(
    identifier: str,
    code: str,
    code_type: str = "email",
    expires_in: int = 3600
) -> bool:
    """Store verification code in Redis."""
    try:
        redis_client = get_redis()
        key = f"verification:{code_type}:{identifier}"
        redis_client.setex(key, expires_in, code)
        return True
    except Exception:
        return False


def verify_code(identifier: str, code: str, code_type: str = "email") -> bool:
    """Verify a code against stored value."""
    try:
        redis_client = get_redis()
        key = f"verification:{code_type}:{identifier}"
        stored_code = redis_client.get(key)
        if stored_code and stored_code.decode('utf-8') == code:
            # Delete code after successful verification
            redis_client.delete(key)
            return True
        return False
    except Exception:
        return False


def send_verification_email(email: str, code: str) -> bool:
    """Send verification email (stub - integrate with email service)."""
    # TODO: Integrate with actual email service (SendGrid, SES, etc.)
    # For now, just log it
    print(f"[EMAIL] Verification code for {email}: {code}")
    return True


def send_verification_sms(phone: str, code: str) -> bool:
    """Send verification SMS (stub - integrate with SMS service)."""
    # TODO: Integrate with actual SMS service (Twilio, etc.)
    # For now, just log it
    print(f"[SMS] Verification code for {phone}: {code}")
    return True

