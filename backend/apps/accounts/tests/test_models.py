import pytest
import uuid
from apps.accounts.models import User, RoleChoices, StatusChoices

@pytest.mark.django_db
def test_user_creation_fields_and_defaults():
    user = User.objects.create_user(
        email='shipper@tradeflow.et',
        password='SecurePassword123!',
        first_name='Abebe',
        last_name='Bikila',
        phone_number='+251911223344'
    )
    assert isinstance(user.id, uuid.UUID)
    assert user.email == 'shipper@tradeflow.et'
    assert user.first_name == 'Abebe'
    assert user.last_name == 'Bikila'
    assert user.phone_number == '+251911223344'
    assert user.role == RoleChoices.SHIPPER
    assert user.status == StatusChoices.PENDING
    assert user.is_verified is False
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert str(user) == 'shipper@tradeflow.et'
    assert user.get_full_name() == 'Abebe Bikila'
    assert user.get_short_name() == 'Abebe'
    assert user.created_at is not None
    assert user.updated_at is not None


@pytest.mark.django_db
def test_user_email_uniqueness():
    User.objects.create_user(email='unique@tradeflow.et', password='Password123!')
    with pytest.raises(Exception):
        User.objects.create_user(email='unique@tradeflow.et', password='Password456!')


@pytest.mark.django_db
def test_user_role_and_status_choices():
    user = User.objects.create_user(
        email='driver@tradeflow.et',
        password='Password123!',
        role=RoleChoices.DRIVER,
        status=StatusChoices.ACTIVE
    )
    assert user.role == 'DRIVER'
    assert user.status == 'ACTIVE'


@pytest.mark.django_db
def test_verification_and_active_isolation():
    user = User.objects.create_user(
        email='transporter@tradeflow.et',
        password='Password123!',
        role=RoleChoices.TRANSPORTER,
        status=StatusChoices.SUSPENDED,
        is_verified=True,
        is_active=False
    )
    assert user.is_verified is True
    assert user.is_active is False
    assert user.status == StatusChoices.SUSPENDED
