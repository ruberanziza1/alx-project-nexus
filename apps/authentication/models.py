# apps/authentication/models.py

"""
Authentication Models

This module contains all models related to user authentication and management.
Includes custom User model, OTP verification, and user profile.
"""

import uuid
import random
import string
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import EmailValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


class UserManager(BaseUserManager):
    """
    Custom user manager for creating users and superusers.
    Handles user creation with email as the primary identifier.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        
        extra_fields.setdefault('role', 'admin')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        extra_fields.setdefault('can_login', True)
        

        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that uses email as the primary identifier.
    """
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, validators=[EmailValidator()])
    
    # User information
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = PhoneNumberField(blank=True, null=True, unique=True)
    

    # User role field
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    # Account status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    can_login = models.BooleanField(default=False)  # Only true after email verification
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Profile fields
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Manager
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['-date_joined']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.email.split('@')[0]


class OTPVerification(models.Model):
    """
    Model to store OTP (One-Time Password) for email verification.
    """
    
    EMAIL = 'email'
    PASSWORD_RESET = 'password_reset'
    
    OTP_TYPE_CHOICES = [
        (EMAIL, 'Email Verification'),
        (PASSWORD_RESET, 'Password Reset'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'OTP Verification'
        verbose_name_plural = 'OTP Verifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'otp_type', '-created_at']),
            models.Index(fields=['otp', 'is_used']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.otp_type} - {self.otp}"
    
    def save(self, *args, **kwargs):
        """Override save to set expiration time."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=getattr(settings, 'OTP_EXPIRY_TIME', 10))
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if the OTP has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if the OTP is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired
    
    @classmethod
    def generate_otp(cls, length=6):
        """Generate a random OTP."""
        return ''.join(random.choices(string.digits, k=length))
    
    @classmethod
    def create_otp(cls, user, otp_type):
        """Create a new OTP for the user."""
        # Invalidate existing unused OTPs
        cls.objects.filter(
            user=user,
            otp_type=otp_type,
            is_used=False
        ).update(is_used=True)
        
        # Generate new OTP
        otp = cls.generate_otp()
        
        return cls.objects.create(user=user, otp=otp, otp_type=otp_type)
    
    def verify(self, otp_code):
        """Verify the OTP code."""
        self.attempts += 1
        self.save()
        
        if self.otp == otp_code and self.is_valid:
            self.is_used = True
            self.save()
            
            # Update user verification status
            if self.otp_type == self.EMAIL:
                self.user.email_verified = True
                self.user.can_login = True
                self.user.save(update_fields=['email_verified', 'can_login'])
            
            return True
        return False


class LoginAttempt(models.Model):
    """Track login attempts for security purposes."""
    
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    is_successful = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    failure_reason = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['email', '-attempted_at']),
            models.Index(fields=['ip_address', '-attempted_at']),
        ]
    
    def __str__(self):
        status = "successful" if self.is_successful else "failed"
        return f"{self.email} - {status} - {self.attempted_at}"
    
    @classmethod
    def check_rate_limit(cls, email, ip_address, window_minutes=15, max_attempts=5):
        """Check if the user has exceeded the rate limit for login attempts."""
        time_threshold = timezone.now() - timedelta(minutes=window_minutes)
        
        email_attempts = cls.objects.filter(
            email=email,
            is_successful=False,
            attempted_at__gte=time_threshold
        ).count()
        
        ip_attempts = cls.objects.filter(
            ip_address=ip_address,
            is_successful=False,
            attempted_at__gte=time_threshold
        ).count()
        
        return email_attempts >= max_attempts or ip_attempts >= max_attempts