from apps.accounts.models import RoleChoices
from apps.core.exceptions import ValidationException
from apps.profiles.models import (
    ShipperProfile,
    TransporterProfile,
    DriverProfile,
    FreightForwarderProfile,
    CustomsStaffProfile,
)

def get_or_create_user_profile(user):
    """
    Returns (profile_obj, serializer_class) for user based on user's role.
    """
    role = user.role
    if role == RoleChoices.SHIPPER:
        profile, _ = ShipperProfile.objects.get_or_create(user=user)
        from apps.profiles.serializers import ShipperProfileSerializer
        return profile, ShipperProfileSerializer

    elif role == RoleChoices.TRANSPORTER:
        profile, _ = TransporterProfile.objects.get_or_create(user=user)
        from apps.profiles.serializers import TransporterProfileSerializer
        return profile, TransporterProfileSerializer

    elif role == RoleChoices.DRIVER:
        profile, _ = DriverProfile.objects.get_or_create(user=user)
        from apps.profiles.serializers import DriverProfileSerializer
        return profile, DriverProfileSerializer

    elif role == RoleChoices.FREIGHT_FORWARDER:
        profile, _ = FreightForwarderProfile.objects.get_or_create(user=user)
        from apps.profiles.serializers import FreightForwarderProfileSerializer
        return profile, FreightForwarderProfileSerializer

    elif role == RoleChoices.CUSTOMS_STAFF:
        profile, _ = CustomsStaffProfile.objects.get_or_create(user=user)
        from apps.profiles.serializers import CustomsStaffProfileSerializer
        return profile, CustomsStaffProfileSerializer

    else:
        raise ValidationException(f"No business profile configured for role {role}.")


def update_user_profile(user, data):
    """
    Updates the authenticated user's profile with validated data.
    """
    profile, serializer_class = get_or_create_user_profile(user)
    serializer = serializer_class(profile, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer.data
