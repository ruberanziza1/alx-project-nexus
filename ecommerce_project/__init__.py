# ecommerce_project/__init__.py

"""
E-commerce Project Initialization

This ensures Celery is loaded when Django starts.
"""

# Conditional import to prevent errors if Celery is not installed
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery is not installed, continue without it
    pass