# apps/authentication/admin.py

"""
Authentication Admin Configuration

This module configures the Django admin interface for authentication models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, OTPVerification, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin configuration.
    """
    
    list_display = [
        'email', 
        'first_name', 
        'last_name', 
        'email_verified', 
        'can_login',
        'is_active', 
        'is_staff', 
        'date_joined'
    ]
    
    list_filter = [
        'email_verified', 
        'can_login',
        'is_active', 
        'is_staff', 
        'is_superuser', 
        'date_joined'
    ]
    
    search_fields = ['email', 'first_name', 'last_name']
    
    ordering = ['-date_joined']
    
    readonly_fields = ['id', 'date_joined', 'last_login', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar', 'bio')
        }),
        ('Verification Status', {
            'fields': ('email_verified', 'can_login')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('date_joined', 'last_login', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    """
    OTP Verification admin configuration.
    """
    
    list_display = [
        'user', 
        'otp_type', 
        'otp_display',
        'is_used', 
        'is_expired_display',
        'attempts',
        'created_at'
    ]
    
    list_filter = ['otp_type', 'is_used', 'created_at']
    
    search_fields = ['user__email', 'otp']
    
    readonly_fields = ['id', 'otp', 'created_at', 'expires_at', 'attempts']
    
    ordering = ['-created_at']
    
    def otp_display(self, obj):
        """Display OTP with masking for security."""
        if obj.otp:
            return f"***{obj.otp[-2:]}"
        return "N/A"
    otp_display.short_description = 'OTP'
    
    def is_expired_display(self, obj):
        """Display expiration status with color coding."""
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_display.short_description = 'Status'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """
    Login Attempt admin configuration.
    """
    
    list_display = [
        'email', 
        'ip_address', 
        'is_successful', 
        'failure_reason',
        'attempted_at'
    ]
    
    list_filter = ['is_successful', 'attempted_at']
    
    search_fields = ['email', 'ip_address']
    
    readonly_fields = ['email', 'ip_address', 'user_agent', 'is_successful', 'failure_reason', 'attempted_at']
    
    ordering = ['-attempted_at']
    
    def has_add_permission(self, request):
        """Disable adding login attempts manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing login attempts."""
        return False