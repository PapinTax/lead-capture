from pydantic import BaseModel, EmailStr
from typing import Any, Optional
import datetime


class SubmissionRequest(BaseModel):
    email: EmailStr
    form_data: dict[str, Any] = {}
    form_version: str = "unknown"
    is_test: bool = False


class SubmissionRecord(BaseModel):
    id: int
    email: str
    form_data: dict[str, Any]
    form_version: str
    is_test: bool
    timestamp: datetime.datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    referrer: Optional[str]
