# apps/authentication/tasks.py

"""
Celery Tasks for Authentication

Asynchronous tasks for email sending and other background operations.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_otp_email(self, user_id, otp_code, otp_type='email'):
    """
    Send OTP verification email asynchronously.
    
    Args:
        user_id (str): User's ID
        otp_code (str): OTP code to send
        otp_type (str): Type of OTP (email, phone, password_reset)
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        from .models import User
        
        # Get user
        user = User.objects.get(id=user_id)
        
        # Prepare email context
        context = {
            'user_name': user.get_full_name(),
            'user_email': user.email,
            'otp_code': otp_code,
            'expiry_minutes': settings.OTP_EXPIRY_TIME,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL
        }
        
        # Choose template based on OTP type
        if otp_type == 'password_reset':
            template_name = 'password_reset'
            subject = f'Password Reset Request - {settings.SITE_NAME}'
        else:
            template_name = 'otp_verification'
            subject = f'Verify Your Email - {settings.SITE_NAME}'
        
        # Render email content
        html_content = render_to_string(f'emails/{template_name}.html', context)
        text_content = strip_tags(html_content)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False
        )
        
        logger.info(f"OTP email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email: {str(e)}")
        # Retry the task
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id):
    """
    Send welcome email to newly verified users.
    
    Args:
        user_id (str): User's ID
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        from .models import User
        
        # Get user
        user = User.objects.get(id=user_id)
        
        # Prepare email context
        context = {
            'user_name': user.get_full_name(),
            'user_email': user.email,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL
        }
        
        # Render email content
        html_content = render_to_string('emails/welcome.html', context)
        text_content = strip_tags(html_content)
        
        # Send email
        send_mail(
            subject=f'Welcome to {settings.SITE_NAME}!',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False
        )
        
        logger.info(f"Welcome email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def cleanup_expired_otps():
    """
    Clean up expired OTP records from the database.
    This task should be run periodically (e.g., daily).
    """
    from .models import OTPVerification
    
    expired_count = OTPVerification.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()[0]
    
    logger.info(f"Cleaned up {expired_count} expired OTP records")
    return expired_count


@shared_task
def cleanup_old_login_attempts():
    """
    Clean up old login attempt records (older than 30 days).
    This task should be run periodically.
    """
    from .models import LoginAttempt
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = LoginAttempt.objects.filter(
        attempted_at__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old login attempt records")
    return deleted_count