from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView

from apps.core.responses import success_response
from apps.accounts.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    LogoutSerializer,
    UserSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from apps.accounts.services import (
    register_user,
    authenticate_user,
    blacklist_refresh_token,
    change_password,
    request_password_reset,
    confirm_password_reset,
)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    @extend_schema(request=UserRegisterSerializer, responses={201: UserSerializer})
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = register_user(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
            phone_number=data.get('phone_number', '')
        )
        return success_response(
            data=UserSerializer(user).data,
            message="User registered successfully. Pending account verification.",
            status_code=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(request=UserLoginSerializer)
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        auth_data = authenticate_user(
            email=data['email'],
            password=data['password']
        )
        payload = {
            "access": auth_data["access"],
            "refresh": auth_data["refresh"],
            "user": UserSerializer(auth_data["user"]).data,
        }
        return success_response(
            data=payload,
            message="Authentication successful."
        )


class CustomTokenRefreshView(SimpleJWTTokenRefreshView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(request=LogoutSerializer)
    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        blacklist_refresh_token(serializer.validated_data['refresh'])
        return success_response(message="Logged out successfully.")


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(responses={200: UserSerializer})
    def get(self, request, *args, **kwargs):
        return success_response(data=UserSerializer(request.user).data)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    @extend_schema(request=PasswordChangeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        change_password(
            user=request.user,
            old_password=data['old_password'],
            new_password=data['new_password']
        )
        return success_response(message="Password changed successfully.")


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    @extend_schema(request=PasswordResetRequestSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = request_password_reset(serializer.validated_data['email'])
        response_data = {}
        if result:
            response_data = result
        return success_response(
            data=response_data,
            message="If an account with that email exists, password reset instructions have been generated."
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    @extend_schema(request=PasswordResetConfirmSerializer)
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        token_val = data['token']
        if ':' in token_val:
            uidb64, token = token_val.split(':', 1)
        else:
            uidb64, token = token_val, token_val

        user = confirm_password_reset(
            uidb64=uidb64,
            token=token,
            new_password=data['new_password']
        )
        return success_response(
            data=UserSerializer(user).data,
            message="Password has been reset successfully."
        )
