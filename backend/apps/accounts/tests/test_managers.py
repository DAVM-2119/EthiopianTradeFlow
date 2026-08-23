import pytest
from apps.accounts.models import User, RoleChoices, StatusChoices

@pytest.mark.django_db
def test_create_user_email_normalization_and_password_hashing():
    raw_password = 'MySecretPassword123!'
    user = User.objects.create_user(
        email='TEST.USER@TRADEFLOW.ET',
        password=raw_password
    )
    assert user.email == 'TEST.USER@tradeflow.et'
    assert user.password != raw_password
    assert user.check_password(raw_password) is True
    assert user.check_password('WrongPassword') is False


@pytest.mark.django_db
def test_create_user_without_email_raises_value_error():
    with pytest.raises(ValueError, match="The Email field must be set"):
        User.objects.create_user(email='', password='Password123!')


@pytest.mark.django_db
def test_create_superuser_success_and_validation():
    admin_user = User.objects.create_superuser(
        email='admin@tradeflow.et',
        password='AdminPassword123!'
    )
    assert admin_user.is_staff is True
    assert admin_user.is_superuser is True
    assert admin_user.is_active is True
    assert admin_user.status == StatusChoices.ACTIVE
    assert admin_user.role == RoleChoices.ADMIN

    with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
        User.objects.create_superuser(
            email='invalid_staff@tradeflow.et',
            password='Password123!',
            is_staff=False
        )

    with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
        User.objects.create_superuser(
            email='invalid_super@tradeflow.et',
            password='Password123!',
            is_superuser=False
        )
