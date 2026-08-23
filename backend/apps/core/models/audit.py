from django.db import models
from .base import BaseModel

class ActionChoices(models.TextChoices):
    CREATE = 'CREATE', 'Create'
    UPDATE = 'UPDATE', 'Update'
    DELETE = 'DELETE', 'Delete'
    LOGIN = 'LOGIN', 'Login'
    LOGOUT = 'LOGOUT', 'Logout'
    VERIFY = 'VERIFY', 'Verify'
    REJECT = 'REJECT', 'Reject'
    CUSTOM = 'CUSTOM', 'Custom'

class AuditLog(BaseModel):
    """
    Reusable system audit log model tracking WHO, WHAT, WHEN, and WHICH resource
    without tight coupling to authentication/user models.
    """
    actor_id = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        null=True,
        help_text="Identifier of the user, system process, or client performing the action"
    )
    action = models.CharField(
        max_length=50,
        choices=ActionChoices.choices,
        default=ActionChoices.CUSTOM,
        db_index=True,
        help_text="Action type (e.g. CREATE, UPDATE, DELETE, VERIFY)"
    )
    resource_type = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Target resource type (e.g. User, Load, Shipment)"
    )
    resource_id = models.CharField(
        max_length=255,
        db_index=True,
        blank=True,
        null=True,
        help_text="Target resource primary key / UUID identifier"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured contextual metadata (excluding sensitive credentials/keys)"
    )

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['actor_id', 'action']),
        ]

    def __str__(self):
        return f"[{self.action}] {self.resource_type}:{self.resource_id or 'N/A'} by {self.actor_id or 'system'} at {self.created_at}"
