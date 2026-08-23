from typing import Optional
from .base import BaseFuelDataProvider, TelematicsFuelData

class ManualFuelDataProvider(BaseFuelDataProvider):
    """
    Manual / Default telematics provider fallback.
    """
    def fetch_trip_telematics_fuel(self, shipment_id: str) -> Optional[TelematicsFuelData]:
        return None
