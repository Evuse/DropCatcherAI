import time
import httpx
import json
from app.registrars.base import BaseRegistrar, RegistrationResult
from app.config import settings

class OpenproviderRegistrar(BaseRegistrar):
    def __init__(self):
        self.api_token = settings.OPENPROVIDER_API_TOKEN
        self.base_url = "https://api.openprovider.eu/v1beta"

    async def register_domain(self, domain: str) -> RegistrationResult:
        start_time = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            # Parse additional data if provided
            additional_data = {}
            if settings.OPENPROVIDER_IT_ADDITIONAL_DATA_JSON:
                try:
                    additional_data = json.loads(settings.OPENPROVIDER_IT_ADDITIONAL_DATA_JSON)
                except:
                    pass

            parts = domain.split(".")
            name = parts[0]
            extension = ".".join(parts[1:])

            payload = {
                "domain": {
                    "name": name,
                    "extension": extension
                },
                "period": 1,
                "ownerHandle": settings.OPENPROVIDER_OWNER_HANDLE,
                "adminHandle": settings.OPENPROVIDER_ADMIN_HANDLE,
                "techHandle": settings.OPENPROVIDER_TECH_HANDLE,
                "billingHandle": settings.OPENPROVIDER_BILLING_HANDLE,
                "nameServerGroup": settings.OPENPROVIDER_NAMESERVER_GROUP,
                "additionalData": additional_data
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/domains", 
                    headers=headers, 
                    json=payload, 
                    timeout=10.0
                )
                latency = int((time.time() - start_time) * 1000)
                
                try:
                    data = response.json()
                    success = response.status_code in (200, 201) and data.get("code") == 0
                    message = data.get("desc", f"HTTP {response.status_code}")
                except:
                    success = False
                    message = f"HTTP {response.status_code}"
                
                return RegistrationResult(
                    success=success,
                    domain=domain,
                    registrar="openprovider",
                    message=message,
                    latency_ms=latency,
                    raw=response.text
                )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return RegistrationResult(
                success=False,
                domain=domain,
                registrar="openprovider",
                message=str(e),
                latency_ms=latency,
                raw=""
            )
