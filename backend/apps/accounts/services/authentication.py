from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from apps.accounts.models import User, StatusChoices
from apps.core.exceptions import ValidationException, PermissionDeniedException

def authenticate_user(email, password):
    """
    Authenticates user credentials and checks account status.
    Generates generic validation error on bad credentials to prevent account enumeration.
    """
    user = User.objects.filter(email__iexact=email.strip()).first()
    if not user or not user.check_password(password):
        raise ValidationException("Invalid email or password.")

    if not user.is_active:
        raise PermissionDeniedException("Account is inactive.")

    if user.status == StatusChoices.SUSPENDED:
        raise PermissionDeniedException("Account has been suspended.")

    if user.status == StatusChoices.INACTIVE:
        raise PermissionDeniedException("Account is inactive.")

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": user,
    }


def blacklist_refresh_token(token_string):
    """
    Blacklists a refresh token using SimpleJWT blacklist.
    """
    try:
        token = RefreshToken(token_string)
        token.blacklist()
        return True
    except Exception as e:
        raise ValidationException(f"Invalid or expired refresh token: {str(e)}")


def change_password(user, old_password, new_password):
    """
    Changes user password and updates credential security.
    """
    if not user.check_password(old_password):
        raise ValidationException("Incorrect old password.")

    user.set_password(new_password)
    user.save()
    return True


def request_password_reset(email):
    """
    Generates a password reset token for the user if exists. Returns generic success state.
    """
    user = User.objects.filter(email__iexact=email.strip()).first()
    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return {"uid": uid, "token": token}
    return None


def confirm_password_reset(uidb64, token, new_password):
    """
    Validates password reset token and updates password.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise ValidationException("Invalid password reset link or expired token.")

    if not default_token_generator.check_token(user, token):
        raise ValidationException("Invalid or expired password reset token.")

    user.set_password(new_password)
    user.save()
    return user
