# apps/authentication/serializers.py

"""
Authentication Serializers

This module contains all serializers for authentication endpoints.
Handles validation, serialization, and deserialization of auth data.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import User, OTPVerification, LoginAttempt


# ============================================================================
# AUTHENTICATION SERIALIZERS
# ============================================================================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Creates a new user account and requires OTP verification before login.
    """
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        email = value.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        attrs.pop('password_confirm')
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create user with email verification required."""
        validated_data['role'] = 'customer'  # Always default to customer
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and enforces email verification requirement.
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    ip_address = serializers.IPAddressField(required=False, write_only=True)
    user_agent = serializers.CharField(required=False, write_only=True)
    
    def validate_email(self, value):
        """Normalize email to lowercase."""
        return value.lower().strip()
    
    def validate(self, attrs):
        """Validate login credentials and verification status."""
        email = attrs.get('email')
        password = attrs.get('password')
        ip_address = attrs.get('ip_address')
        
        # Check rate limiting
        if ip_address and LoginAttempt.check_rate_limit(email, ip_address):
            raise serializers.ValidationError("Too many login attempts. Please try again later.")
        
        # Authenticate user
        user = authenticate(email=email, password=password)
        
        # Track login attempt
        if ip_address:
            LoginAttempt.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=attrs.get('user_agent', ''),
                is_successful=bool(user),
                failure_reason='' if user else 'Invalid credentials'
            )
        
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("Your account has been deactivated.")
        
        # Check email verification requirement
        if not user.email_verified or not user.can_login:
            raise serializers.ValidationError("Please verify your email before logging in.")
        
        attrs['user'] = user
        return attrs


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification."""
    
    otp = serializers.CharField(min_length=6, max_length=6)
    otp_type = serializers.ChoiceField(
        choices=OTPVerification.OTP_TYPE_CHOICES,
        default=OTPVerification.EMAIL
    )
    
    def validate_otp(self, value):
        """Validate OTP format."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only numbers.")
        return value
    
    def validate(self, attrs):
        """Validate OTP against database."""
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User context is required.")
        
        otp_code = attrs.get('otp')
        otp_type = attrs.get('otp_type')
        
        # Find the latest valid OTP
        otp_instance = OTPVerification.objects.filter(
            user=user,
            otp_type=otp_type,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp_instance:
            raise serializers.ValidationError("No valid OTP found. Please request a new one.")
        
        if otp_instance.is_expired:
            raise serializers.ValidationError("OTP has expired. Please request a new one.")
        
        if otp_instance.attempts >= 3:
            raise serializers.ValidationError("Maximum verification attempts exceeded.")
        
        # Verify OTP
        if not otp_instance.verify(otp_code):
            remaining = 3 - otp_instance.attempts
            raise serializers.ValidationError(f"Invalid OTP. {remaining} attempts remaining.")
        
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP."""
    
    otp_type = serializers.ChoiceField(
        choices=OTPVerification.OTP_TYPE_CHOICES,
        default=OTPVerification.EMAIL
    )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset."""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Normalize email."""
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset with OTP."""
    
    otp = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that uses email and includes user data."""
    
    username_field = 'email'
    
    def validate(self, attrs):
        """Override to use email and check verification status."""
        attrs['email'] = attrs.get('email', '').lower().strip()
        
        # Check if user exists and is verified before authentication
        try:
            user = User.objects.get(email=attrs['email'])
            if not user.email_verified or not user.can_login:
                raise serializers.ValidationError("Please verify your email before logging in.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email_verified': self.user.email_verified
        }
        
        return data


# ============================================================================
# PROFILE SERIALIZERS
# ============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile management."""
    
    full_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'email_verified',
            'role',
            'avatar',
            'bio',
            'date_joined',
            'last_login'
        ]
        read_only_fields = [
            'id',
            'email',
            'email_verified',
            'role',
            'date_joined',
            'last_login'
        ]
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return obj.get_full_name()
    
def validate_phone_number(self, value):
    """Validate phone number uniqueness."""
    if value:
        # Get user from context more safely
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if User.objects.filter(phone_number=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("This phone number is already registered.")
        # If no request context, get user from instance (for updates)
        elif hasattr(self, 'instance') and self.instance:
            user = self.instance
            if User.objects.filter(phone_number=value).exclude(id=user.id).exists():
                raise serializers.ValidationError("This phone number is already registered.")
    return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password when user is logged in."""
    
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context.get('request').user
        if not user.check_password(value):
            raise serializers.ValidationError("Your old password is incorrect.")
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate passwords match and are different."""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        old_password = attrs.get('old_password')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({'new_password_confirm': 'New passwords do not match.'})
        
        if old_password == new_password:
            raise serializers.ValidationError({'new_password': 'New password must be different from old password.'})
        
        return attrs