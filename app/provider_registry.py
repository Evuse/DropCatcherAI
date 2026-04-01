from app.config import settings
from app.registrars.dynadot_registrar import DynadotRegistrar
from app.registrars.openprovider_registrar import OpenproviderRegistrar
from app.registrars.gandi_registrar import GandiRegistrar

AVAILABLE_PROVIDER_NAMES = ["dynadot", "openprovider", "gandi"]

def get_active_providers():
    providers = {}
    if settings.DYNADOT_ENABLED:
        providers["dynadot"] = DynadotRegistrar()
    if settings.OPENPROVIDER_ENABLED:
        providers["openprovider"] = OpenproviderRegistrar()
    if settings.GANDI_ENABLED:
        providers["gandi"] = GandiRegistrar()
    return providers
