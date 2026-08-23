from dataclasses import dataclass
from typing import Optional

@dataclass
class TelematicsFuelData:
    distance_km: float
    fuel_consumed_liters: float
    data_source: str = 'TELEMATICS'


class BaseFuelDataProvider:
    """
    Abstract interface for telematics sensor fuel data ingestion boundaries.
    """
    def fetch_trip_telematics_fuel(self, shipment_id: str) -> Optional[TelematicsFuelData]:
        raise NotImplementedError("Subclasses must implement fetch_trip_telematics_fuel()")
