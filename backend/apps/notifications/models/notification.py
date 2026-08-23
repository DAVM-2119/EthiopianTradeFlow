from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class NotificationTypeChoices(models.TextChoices):
    SHIPMENT_DEPARTED = 'SHIPMENT_DEPARTED', 'Shipment Departed'
    SHIPMENT_CUSTOMS_CLEARED = 'SHIPMENT_CUSTOMS_CLEARED', 'Shipment Customs Cleared'
    SHIPMENT_ARRIVED = 'SHIPMENT_ARRIVED', 'Shipment Arrived Destination'
    SHIPMENT_DELIVERED = 'SHIPMENT_DELIVERED', 'Shipment Delivered'
    
    PAYMENT_COMPLETED = 'PAYMENT_COMPLETED', 'Payment Completed'
    PAYMENT_FAILED = 'PAYMENT_FAILED', 'Payment Failed'
    PAYOUT_PROCESSED = 'PAYOUT_PROCESSED', 'Payout Processed'
    
    SECURITY_ALERT = 'SECURITY_ALERT', 'Security Alert'
    
    DISPUTE_CREATED = 'DISPUTE_CREATED', 'Dispute Created'
    DISPUTE_RESOLVED = 'DISPUTE_RESOLVED', 'Dispute Resolved'
    
    BOOKING_CONFIRMED = 'BOOKING_CONFIRMED', 'Booking Confirmed'
    BOOKING_CANCELLED = 'BOOKING_CANCELLED', 'Booking Cancelled'
    
    SYSTEM_ALERT = 'SYSTEM_ALERT', 'System Alert'


class NotificationChannelChoices(models.TextChoices):
    IN_APP = 'IN_APP', 'In-App Notification'
    EMAIL = 'EMAIL', 'Email Notification'
    SMS = 'SMS', 'SMS Notification'
    PUSH = 'PUSH', 'Push Notification'


class NotificationStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    SENT = 'SENT', 'Sent'
    FAILED = 'FAILED', 'Failed'
    RETRYING = 'RETRYING', 'Retrying'


class NotificationPriorityChoices(models.TextChoices):
    LOW = 'LOW', 'Low'
    NORMAL = 'NORMAL', 'Normal'
    HIGH = 'HIGH', 'High'
    CRITICAL = 'CRITICAL', 'Critical'


class Notification(BaseModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True
    )
    notification_type = models.CharField(
        max_length=40,
        choices=NotificationTypeChoices.choices,
        db_index=True
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannelChoices.choices,
        default=NotificationChannelChoices.IN_APP,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatusChoices.choices,
        default=NotificationStatusChoices.PENDING,
        db_index=True
    )
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriorityChoices.choices,
        default=NotificationPriorityChoices.NORMAL
    )

    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.CharField(max_length=100, blank=True)
    data = models.JSONField(default=dict, blank=True)

    idempotency_key = models.CharField(
        max_length=150,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        help_text="Unique event key to prevent duplicate notifications"
    )

    read = models.BooleanField(default=False, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'read']),
            models.Index(fields=['recipient', 'status']),
        ]

    def __str__(self):
        return f"Notification [{self.channel}] -> {self.recipient.email}: {self.title}"
