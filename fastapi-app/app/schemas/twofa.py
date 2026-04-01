from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TwoFaSettings(BaseModel):
    enabled: bool = False
    method: str = "email"  # or 'sms'
    enforced: bool = False


class TwoFaCheckRequest(BaseModel):
    identity: str


class TwoFaCheckResponse(BaseModel):
    twoFaSession: Optional[str] = None
    isTwoFaEnabled: bool


class TwoFaValidateRequest(BaseModel):
    token: str
    identity: str
    clientToken: Optional[str] = None


class TwoFaValidateResponse(BaseModel):
    clientToken: Optional[str] = None
    expired: bool


class TwoFaVerifyRequest(BaseModel):
    code: str
    token: str
    clientToken: Optional[str] = None


class TwoFaVerifyResponse(BaseModel):
    authToken: str


class TwoFaResendRequest(BaseModel):
    identity: str
    token: str


class TwoFaResendResponse(BaseModel):
    clientToken: str


class TwoFaInvalidateRequest(BaseModel):
    identity: str
    token: str


class TwoFaInvalidateResponse(BaseModel):
    ok: bool


class TwoFaEnforceResponse(BaseModel):
    shouldEnforce: bool



