from apps.accounts.models import User, RoleChoices, StatusChoices

def register_user(email, first_name, last_name, password, phone_number=''):
    """
    Registers a new public user with default non-privileged attributes.
    Enforces role=SHIPPER, status=PENDING, is_verified=False.
    """
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        role=RoleChoices.SHIPPER,
        status=StatusChoices.PENDING,
        is_verified=False,
        is_staff=False,
        is_superuser=False
    )
    return user
