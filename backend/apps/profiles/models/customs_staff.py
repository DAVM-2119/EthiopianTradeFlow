from django.db import models
from django.conf import settings
from apps.core.models import BaseModel

class CustomsStaffProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customs_staff_profile'
    )
    organization = models.CharField(max_length=255, blank=True, default='Ethiopian Customs Commission')
    staff_identifier = models.CharField(max_length=100, blank=True)
    office_location = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Customs Staff Profile'
        verbose_name_plural = 'Customs Staff Profiles'

    def __str__(self):
        return f"Customs Staff: {self.user.get_full_name()} ({self.staff_identifier})"
