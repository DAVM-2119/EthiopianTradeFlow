from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import User

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    phone_number = serializers.CharField(max_length=30, required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        email_normalized = value.strip().lower()
        if User.objects.filter(email__iexact=email_normalized).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return email_normalized

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs
