from app.config import settings
from app.registrars.dynadot_registrar import DynadotRegistrar
from app.registrars.openprovider_registrar import OpenproviderRegistrar

AVAILABLE_PROVIDER_NAMES = ["dynadot", "openprovider"]

def get_active_providers():
    providers = {}
    if settings.DYNADOT_ENABLED:
        providers["dynadot"] = DynadotRegistrar()
    if settings.OPENPROVIDER_ENABLED:
        providers["openprovider"] = OpenproviderRegistrar()
    return providers
