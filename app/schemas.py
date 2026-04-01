from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DomainBase(BaseModel):
    fqdn: str
    expected_drop_at: datetime
    auto_start_window_seconds: int = 60
    burst_duration_seconds: int = 120
    interval_ms: int = 500
    selected_providers: str = ""

class DomainCreate(DomainBase):
    pass

class DomainUpdate(DomainBase):
    status: Optional[str] = None

class DomainResponse(DomainBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
