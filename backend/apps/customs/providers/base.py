from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class CustomsSubmissionResult:
    status: str
    reference_number: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


class BaseCustomsProvider:
    """
    Abstract interface for external customs commission integration boundaries.
    """
    def submit_for_clearance(self, shipment_id: str, document_ids: List[str]) -> CustomsSubmissionResult:
        raise NotImplementedError("Subclasses must implement submit_for_clearance()")
