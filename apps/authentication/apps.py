# apps/authentication/apps.py

"""
Authentication App Configuration
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration for the authentication app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = 'Authentication'
    
    def ready(self):
        """
        Perform initialization when the app is ready.
        """
        # Import signal handlers if any
        pass
