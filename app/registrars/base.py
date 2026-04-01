from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class RegistrationResult:
    success: bool
    domain: str
    registrar: str
    message: str
    latency_ms: int
    raw: str

class BaseRegistrar(ABC):
    @abstractmethod
    async def register_domain(self, domain: str) -> RegistrationResult:
        pass
