from django.urls import path
from .views import (
    ShipmentCustomsDocumentListUploadAPIView,
    CustomsDocumentDetailAPIView,
    ShipmentCustomsValidateAPIView,
    ShipmentCustomsSubmitAPIView,
    ShipmentCustomsStatusAPIView,
)

urlpatterns = [
    path('shipments/<uuid:shipment_id>/customs/documents/', ShipmentCustomsDocumentListUploadAPIView.as_view(), name='shipment-customs-document-list-upload'),
    path('customs/documents/<uuid:document_id>/', CustomsDocumentDetailAPIView.as_view(), name='customs-document-detail'),
    path('shipments/<uuid:shipment_id>/customs/validate/', ShipmentCustomsValidateAPIView.as_view(), name='shipment-customs-validate'),
    path('shipments/<uuid:shipment_id>/customs/submit/', ShipmentCustomsSubmitAPIView.as_view(), name='shipment-customs-submit'),
    path('shipments/<uuid:shipment_id>/customs/status/', ShipmentCustomsStatusAPIView.as_view(), name='shipment-customs-status'),
]
