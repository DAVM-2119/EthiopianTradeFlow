from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class DriverStatusChoices(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    ASSIGNED = 'ASSIGNED', 'Assigned'
    ON_TRIP = 'ON_TRIP', 'On Trip'
    INACTIVE = 'INACTIVE', 'Inactive'


class DriverProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='driver_profile'
    )
    transporter = models.ForeignKey(
        'profiles.TransporterProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='drivers'
    )
    license_number = models.CharField(max_length=100, blank=True, db_index=True)
    license_type = models.CharField(max_length=50, blank=True)
    license_expiry_date = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(
        max_length=20,
        choices=DriverStatusChoices.choices,
        default=DriverStatusChoices.AVAILABLE,
        db_index=True
    )

    class Meta:
        verbose_name = 'Driver Profile'
        verbose_name_plural = 'Driver Profiles'

    def __str__(self):
        return f"Driver: {self.user.get_full_name()} ({self.license_number})"
