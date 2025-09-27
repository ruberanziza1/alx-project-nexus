# apps/common/models.py

"""
Common Models

Base models and mixins used across the application.
"""

from django.db import models
import uuid


class TimeStampedModel(models.Model):
    """
    Abstract base model with created and updated timestamps.
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the record was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the record was last updated"
    )
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model with UUID as primary key.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier"
    )
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base model for soft delete functionality.
    """
    
    is_deleted = models.BooleanField(
        default=False,
        help_text="Indicates if the record is soft deleted"
    )
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the record was deleted"
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        """Soft delete the record."""
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restore a soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()