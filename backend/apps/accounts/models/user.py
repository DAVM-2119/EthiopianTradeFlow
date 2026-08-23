from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.core.models import BaseModel
from apps.accounts.managers import UserManager

class RoleChoices(models.TextChoices):
    SHIPPER = 'SHIPPER', 'Shipper'
    TRANSPORTER = 'TRANSPORTER', 'Transporter'
    DRIVER = 'DRIVER', 'Driver'
    FREIGHT_FORWARDER = 'FREIGHT_FORWARDER', 'Freight Forwarder'
    CUSTOMS_STAFF = 'CUSTOMS_STAFF', 'Customs Staff'
    ADMIN = 'ADMIN', 'Administrator'


class StatusChoices(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    SUSPENDED = 'SUSPENDED', 'Suspended'
    PENDING = 'PENDING', 'Pending'


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for TradeFlow using Email as the primary authentication identifier.
    Inherits UUID primary key (id), created_at, and updated_at from BaseModel.
    """
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name='Email Address',
        help_text='Primary login identifier'
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        db_index=True,
        help_text='Primary contact phone number (e.g. +251...)'
    )
    role = models.CharField(
        max_length=30,
        choices=RoleChoices.choices,
        default=RoleChoices.SHIPPER,
        db_index=True,
        help_text='User primary role on the platform'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
        help_text='Account lifecycle status'
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Platform identity & business documentation verification state'
    )

    # Standard Django Admin & Permission flags
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user account should be treated as active in Django auth'
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the Django admin site'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['email', 'status']),
        ]

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email

    def get_short_name(self):
        return self.first_name or self.email

    def __str__(self):
        return self.email
