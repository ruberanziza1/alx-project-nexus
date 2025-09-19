# apps/common/exceptions.py

"""
Custom Exception Handlers

This module contains custom exception handling for the API.
Provides consistent error response format across the application.
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats all errors consistently.
    
    Args:
        exc: The exception instance
        context: The context dictionary
        
    Returns:
        Response: Formatted error response
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'success': False,
            'message': 'An error occurred',
            'errors': {},
            'status_code': response.status_code
        }
        
        # Handle different types of responses
        if isinstance(response.data, dict):
            # Extract error messages
            for field, value in response.data.items():
                if field == 'detail':
                    custom_response_data['message'] = str(value)
                elif field == 'non_field_errors':
                    custom_response_data['message'] = ' '.join(
                        [str(v) for v in value] if isinstance(value, list) else [str(value)]
                    )
                else:
                    # Field-specific errors
                    custom_response_data['errors'][field] = (
                        value if isinstance(value, list) else [value]
                    )
        elif isinstance(response.data, list):
            custom_response_data['message'] = ' '.join([str(item) for item in response.data])
        else:
            custom_response_data['message'] = str(response.data)
        
        # Add request ID for tracking (if available)
        request = context.get('request')
        if request and hasattr(request, 'id'):
            custom_response_data['request_id'] = request.id
        
        response.data = custom_response_data
    
    # Log the exception
    if exc:
        logger.error(
            f"API Exception: {exc.__class__.__name__}: {str(exc)}",
            exc_info=True,
            extra={
                'request': context.get('request'),
                'view': context.get('view')
            }
        )
    
    return response


class CustomAPIException(APIException):
    """
    Base custom API exception class.
    All custom exceptions should inherit from this.
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred.'
    default_code = 'error'
    
    def __init__(self, detail=None, code=None, status_code=None):
        """
        Initialize custom exception.
        
        Args:
            detail: Error message
            code: Error code
            status_code: HTTP status code
        """
        if status_code is not None:
            self.status_code = status_code
        
        super().__init__(detail, code)


class ValidationException(CustomAPIException):
    """Exception raised for validation errors."""
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation failed.'
    default_code = 'validation_error'


class AuthenticationException(CustomAPIException):
    """Exception raised for authentication errors."""
    
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed.'
    default_code = 'authentication_error'


class PermissionException(CustomAPIException):
    """Exception raised for permission errors."""
    
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_error'


class NotFoundException(CustomAPIException):
    """Exception raised when a resource is not found."""
    
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'not_found'


class ConflictException(CustomAPIException):
    """Exception raised for conflict errors (e.g., duplicate resources)."""
    
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflict occurred.'
    default_code = 'conflict'


class RateLimitException(CustomAPIException):
    """Exception raised when rate limit is exceeded."""
    
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded. Please try again later.'
    default_code = 'rate_limit_exceeded'


class ServerException(CustomAPIException):
    """Exception raised for internal server errors."""
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An internal server error occurred.'
    default_code = 'server_error'