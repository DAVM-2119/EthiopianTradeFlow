from rest_framework import serializers
from apps.customs.models import CustomsDocument, CustomsDocumentTypeChoices, CustomsClearanceStatusChoices

class CustomsDocumentSerializer(serializers.ModelSerializer):
    shipment_id = serializers.UUIDField(source='shipment.id', read_only=True)
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True, default=None)

    class Meta:
        model = CustomsDocument
        fields = (
            'id',
            'shipment_id',
            'document_type',
            'file',
            'original_filename',
            'file_size',
            'mime_type',
            'document_number',
            'issue_date',
            'declared_value',
            'quantity',
            'uploaded_by_email',
            'clearance_status',
            'validation_status',
            'validation_notes',
            'rejection_reason',
            'reviewed_by_email',
            'reviewed_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class CustomsDocumentUploadSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=CustomsDocumentTypeChoices.choices)
    file = serializers.FileField()
    document_number = serializers.CharField(required=False, allow_blank=True, max_length=100)
    issue_date = serializers.DateField(required=False, allow_null=True)
    declared_value = serializers.DecimalField(required=False, allow_null=True, max_digits=14, decimal_places=2)
    quantity = serializers.DecimalField(required=False, allow_null=True, max_digits=12, decimal_places=2)


class CustomsValidationResultSerializer(serializers.Serializer):
    valid = serializers.BooleanField()
    validation_status = serializers.CharField()
    errors = serializers.ListField(child=serializers.DictField())
    document_count = serializers.IntegerField()


class CustomsStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        CustomsClearanceStatusChoices.UNDER_REVIEW,
        CustomsClearanceStatusChoices.CLEARED,
        CustomsClearanceStatusChoices.REJECTED
    ])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
