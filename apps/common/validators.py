# apps/common/validators.py

"""
Common Validators

This module contains validation functions used across the application.
Provides reusable validation logic for emails, passwords, phone numbers, etc.
"""

import re
import phonenumbers
from phonenumbers import carrier, geocoder
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError


def validate_email_format(email):
    """
    Validate email format using regex and Django validator.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic regex pattern for email validation
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    if not email_pattern.match(email):
        return False
    
    # Use Django's validator for additional checks
    try:
        django_validate_email(email)
        return True
    except ValidationError:
        return False


def validate_password_strength(password):
    """
    Validate password strength with custom rules.
    
    Password must contain:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    
    Args:
        password (str): Password to validate
        
    Returns:
        list: List of error messages (empty if valid)
    """
    errors = []
    
    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")
    
    # Check for digit
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number.")
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character.")
    
    # Check for common passwords
    common_passwords = [
        'password', '12345678', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', 'dragon'
    ]
    
    if password.lower() in common_passwords:
        errors.append("This password is too common. Please choose a different one.")
    
    return errors


def validate_phone_number(phone_number):
    """
    Validate international phone number format.
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Parse phone number
        parsed_number = phonenumbers.parse(phone_number, None)
        
        # Check if it's a valid number
        if not phonenumbers.is_valid_number(parsed_number):
            return False
        
        # Check if it's a possible number
        if not phonenumbers.is_possible_number(parsed_number):
            return False
        
        return True
    except phonenumbers.NumberParseException:
        return False


def format_phone_number(phone_number):
    """
    Format phone number to international format.
    
    Args:
        phone_number (str): Phone number to format
        
    Returns:
        str: Formatted phone number or original if invalid
    """
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
        return phonenumbers.format_number(
            parsed_number, 
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
    except phonenumbers.NumberParseException:
        return phone_number


def validate_username(username):
    """
    Validate username format.
    
    Username rules:
    - 3-30 characters long
    - Can contain letters, numbers, dots, and underscores
    - Must start with a letter
    - Cannot end with a dot or underscore
    - Cannot have consecutive dots or underscores
    
    Args:
        username (str): Username to validate
        
    Returns:
        list: List of error messages (empty if valid)
    """
    errors = []
    
    # Check length
    if len(username) < 3:
        errors.append("Username must be at least 3 characters long.")
    elif len(username) > 30:
        errors.append("Username cannot be longer than 30 characters.")
    
    # Check allowed characters
    if not re.match(r'^[a-zA-Z0-9._]+$', username):
        errors.append("Username can only contain letters, numbers, dots, and underscores.")
    
    # Must start with a letter
    if username and not username[0].isalpha():
        errors.append("Username must start with a letter.")
    
    # Cannot end with dot or underscore
    if username and username[-1] in '._':
        errors.append("Username cannot end with a dot or underscore.")
    
    # Check for consecutive dots or underscores
    if '..' in username or '__' in username:
        errors.append("Username cannot have consecutive dots or underscores.")
    
    return errors


def validate_age(date_of_birth, minimum_age=13):
    """
    Validate user's age based on date of birth.
    
    Args:
        date_of_birth (date): User's date of birth
        minimum_age (int): Minimum required age
        
    Returns:
        bool: True if age requirement is met, False otherwise
    """
    from datetime import date
    
    today = date.today()
    age = today.year - date_of_birth.year
    
    # Adjust for birthday not yet occurred this year
    if (today.month, today.day) < (date_of_birth.month, date_of_birth.day):
        age -= 1
    
    return age >= minimum_age


def validate_postal_code(postal_code, country_code=None):
    """
    Validate postal/zip code format.
    
    Args:
        postal_code (str): Postal code to validate
        country_code (str): ISO country code (optional)
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Remove spaces and convert to uppercase
    postal_code = postal_code.replace(' ', '').upper()
    
    # Country-specific patterns
    patterns = {
        'US': r'^\d{5}(-\d{4})?$',  # 12345 or 12345-6789
        'CA': r'^[A-Z]\d[A-Z]\d[A-Z]\d$',  # A1A1A1
        'UK': r'^[A-Z]{1,2}\d{1,2}[A-Z]?\d[A-Z]{2}$',  # SW1A 1AA
        'DE': r'^\d{5}$',  # 12345
        'FR': r'^\d{5}$',  # 12345
        'JP': r'^\d{3}-?\d{4}$',  # 123-4567
        'AU': r'^\d{4}$',  # 1234
        'IN': r'^\d{6}$',  # 123456
    }
    
    # If country code provided, use specific pattern
    if country_code and country_code in patterns:
        pattern = patterns[country_code]
        return bool(re.match(pattern, postal_code))
    
    # Generic pattern for any postal code (alphanumeric, 3-10 characters)
    generic_pattern = r'^[A-Z0-9]{3,10}$'
    return bool(re.match(generic_pattern, postal_code))