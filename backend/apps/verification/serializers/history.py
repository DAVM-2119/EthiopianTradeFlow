from rest_framework import serializers
from apps.verification.models import VerificationHistory

class VerificationHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.CharField(source='changed_by.email', read_only=True)

    class Meta:
        model = VerificationHistory
        fields = (
            'id', 'verification', 'previous_status', 'new_status',
            'changed_by', 'changed_by_email', 'reason', 'notes', 'created_at'
        )
        read_only_fields = fields
