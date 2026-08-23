from typing import List
from .base import BaseCustomsProvider, CustomsSubmissionResult

class MockCustomsProvider(BaseCustomsProvider):
    """
    Mock Customs Integration Provider representing the Ethiopian Customs Commission clearance boundary.
    """
    def submit_for_clearance(self, shipment_id: str, document_ids: List[str]) -> CustomsSubmissionResult:
        ref_num = f"ECC-ETH-{shipment_id[:8].upper()}"
        return CustomsSubmissionResult(
            status='UNDER_REVIEW',
            reference_number=ref_num,
            message="Documents queued for Ethiopian Customs Commission review.",
            details={"document_count": len(document_ids)}
        )
