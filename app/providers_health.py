import json
from dataclasses import dataclass
from typing import Dict, Any
from app.config import settings

@dataclass
class ProviderHealth:
    ready: bool
    message: str
    details: Dict[str, Any]

def parse_json_object(json_str: str) -> bool:
    try:
        data = json.loads(json_str)
        return isinstance(data, dict)
    except:
        return False

def get_static_providers_health() -> Dict[str, ProviderHealth]:
    health = {}
    
    # Dynadot
    dyn_ready = True
    dyn_details = {}
    dyn_msg = "Ready"
    
    if not settings.DYNADOT_ENABLED:
        dyn_ready = False
        dyn_msg = "Disabled"
    elif not settings.DYNADOT_API_KEY or not settings.DYNADOT_API_SECRET:
        dyn_ready = False
        dyn_msg = "Missing API credentials"
    elif not settings.DYNADOT_IT_CONTACT_CONFIRMED:
        dyn_ready = False
        dyn_msg = "IT Contact not confirmed in settings"
        
    health["dynadot"] = ProviderHealth(ready=dyn_ready, message=dyn_msg, details=dyn_details)
    
    # Openprovider
    op_ready = True
    op_details = {}
    op_msg = "Ready"
    
    if not settings.OPENPROVIDER_ENABLED:
        op_ready = False
        op_msg = "Disabled"
    elif not settings.OPENPROVIDER_API_TOKEN:
        op_ready = False
        op_msg = "Missing API token"
    elif not all([
        settings.OPENPROVIDER_OWNER_HANDLE,
        settings.OPENPROVIDER_ADMIN_HANDLE,
        settings.OPENPROVIDER_TECH_HANDLE,
        settings.OPENPROVIDER_BILLING_HANDLE
    ]):
        op_ready = False
        op_msg = "Missing one or more handles"
    elif not settings.OPENPROVIDER_IT_CONTACTS_VERIFIED:
        op_ready = False
        op_msg = "IT Contacts not verified in settings"
    elif not parse_json_object(settings.OPENPROVIDER_IT_ADDITIONAL_DATA_JSON):
        op_ready = False
        op_msg = "Invalid JSON in additional data"
        
    health["openprovider"] = ProviderHealth(ready=op_ready, message=op_msg, details=op_details)
    
    return health

def preflight_providers_for_domain(domain: str) -> Dict[str, ProviderHealth]:
    # For now, static health is sufficient as baseline
    # In the future, this could make live API calls to verify domain availability
    return get_static_providers_health()
