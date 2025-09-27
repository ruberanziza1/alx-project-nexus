# apps/common/utils.py

"""
Common Utilities

This module contains utility functions used across the application.
"""

import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import jwt


def generate_random_string(length=32, include_punctuation=False):
    """
    Generate a random string of specified length.
    
    Args:
        length (int): Length of the string
        include_punctuation (bool): Include special characters
        
    Returns:
        str: Random string
    """
    characters = string.ascii_letters + string.digits
    if include_punctuation:
        characters += string.punctuation
    
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_token(user_id: str, token_type: str = 'access', expires_in: int = 3600) -> str:
    """
    Generate a JWT token for a user.
    
    Args:
        user_id (str): User's ID
        token_type (str): Type of token (access, refresh, etc.)
        expires_in (int): Token expiration time in seconds
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': str(user_id),
        'token_type': token_type,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow(),
        'jti': generate_random_string(16)  # JWT ID for tracking
    }
    
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token (str): JWT token to decode
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def send_email(
    subject: str,
    template_name: str,
    context: dict,
    recipient_list: list,
    from_email: str = None
):
    """
    Send an HTML email with a plain text alternative.
    
    Args:
        subject (str): Email subject
        template_name (str): Name of the email template
        context (dict): Context data for the template
        recipient_list (list): List of recipient email addresses
        from_email (str): Sender email address
        
    Returns:
        int: Number of emails sent
    """
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    
    # Render HTML and text content
    html_content = render_to_string(f'emails/{template_name}.html', context)
    text_content = strip_tags(html_content)
    
    # Create email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list
    )
    
    # Attach HTML version
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    return email.send(fail_silently=False)


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: Django request object
        
    Returns:
        str: Client's IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP if there are multiple
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    
    return ip


def get_user_agent(request) -> str:
    """
    Get the user agent string from the request.
    
    Args:
        request: Django request object
        
    Returns:
        str: User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')


def hash_string(value: str) -> str:
    """
    Create a SHA256 hash of a string.
    
    Args:
        value (str): String to hash
        
    Returns:
        str: Hashed string
    """
    return hashlib.sha256(value.encode()).hexdigest()


def verify_hash(value: str, hashed_value: str) -> bool:
    """
    Verify if a string matches its hash.
    
    Args:
        value (str): Original string
        hashed_value (str): Hashed string
        
    Returns:
        bool: True if match, False otherwise
    """
    return hash_string(value) == hashed_value


def calculate_percentage(part: float, whole: float) -> float:
    """
    Calculate percentage with proper handling of edge cases.
    
    Args:
        part (float): Part value
        whole (float): Whole value
        
    Returns:
        float: Percentage value
    """
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format an amount as currency.
    
    Args:
        amount (float): Amount to format
        currency (str): Currency code
        
    Returns:
        str: Formatted currency string
    """
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"