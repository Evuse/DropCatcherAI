import time
import httpx
from app.registrars.base import BaseRegistrar, RegistrationResult
from app.config import settings

class DynadotRegistrar(BaseRegistrar):
    def __init__(self):
        self.api_key = settings.DYNADOT_API_KEY
        self.api_secret = settings.DYNADOT_API_SECRET
        self.base_url = "https://api.dynadot.com/api3.json"

    async def register_domain(self, domain: str) -> RegistrationResult:
        start_time = time.time()
        try:
            params = {
                "key": self.api_key,
                "command": "register",
                "domain": domain,
                "duration": 1
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=10.0)
                latency = int((time.time() - start_time) * 1000)
                
                data = response.json()
                # Simplified check for success
                success = data.get("RegisterResponse", {}).get("ResponseCode") == "0"
                message = data.get("RegisterResponse", {}).get("ResponseHeader", "Unknown response")
                
                return RegistrationResult(
                    success=success,
                    domain=domain,
                    registrar="dynadot",
                    message=message,
                    latency_ms=latency,
                    raw=response.text
                )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return RegistrationResult(
                success=False,
                domain=domain,
                registrar="dynadot",
                message=str(e),
                latency_ms=latency,
                raw=""
            )
