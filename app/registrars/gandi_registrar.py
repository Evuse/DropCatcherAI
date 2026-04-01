import time
import httpx
from app.registrars.base import BaseRegistrar, RegistrationResult
from app.config import settings

class GandiRegistrar(BaseRegistrar):
    def __init__(self):
        self.api_key = settings.GANDI_API_KEY
        self.org_id = settings.GANDI_ORGANIZATION_ID
        self.base_url = "https://api.gandi.net/v5/domain/domains"

    async def register_domain(self, domain: str) -> RegistrationResult:
        start_time = time.time()
        try:
            headers = {
                # Gandi v5 uses Personal Access Tokens (PAT) as Bearer tokens
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Se è specificata un'organizzazione, passiamo il Sharing-Id
            if self.org_id:
                headers["Sharing-Id"] = self.org_id

            payload = {
                "fqdn": domain,
                "duration": 1
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                latency = int((time.time() - start_time) * 1000)
                
                # Gandi restituisce 201 Created o 202 Accepted se la richiesta è presa in carico
                success = response.status_code in (201, 202)
                
                try:
                    data = response.json()
                    message = data.get("message", f"HTTP {response.status_code}")
                except:
                    message = f"HTTP {response.status_code}"
                
                return RegistrationResult(
                    success=success,
                    domain=domain,
                    registrar="gandi",
                    message=message,
                    latency_ms=latency,
                    raw=response.text
                )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return RegistrationResult(
                success=False,
                domain=domain,
                registrar="gandi",
                message=str(e),
                latency_ms=latency,
                raw=""
            )
