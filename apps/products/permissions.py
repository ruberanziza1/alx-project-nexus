# apps/products/permissions.py

"""
Product Permissions

Custom permission classes for product management.
Ensures proper access control for different user types.
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit products.
    Read permissions are allowed for any request (public products list/detail).
    Write permissions are only allowed to admin users.
    """

    def has_permission(self, request, view):
        # Read permissions for all (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for authenticated admin users
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff and 
            request.user.is_active
        )


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission that only allows admin users full access.
    """

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff and 
            request.user.is_active
        )

    def has_object_permission(self, request, view, obj):
        # Admin users can access any product
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_staff and 
            request.user.is_active
        )


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission that allows:
    - Read access to everyone
    - Write access to admin users or object owners
    """

    def has_permission(self, request, view):
        # Read permissions for all
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions for authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions for all
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions for admin or owner
        return (
            request.user and 
            request.user.is_authenticated and 
            (
                request.user.is_staff or 
                (hasattr(obj, 'created_by') and obj.created_by == request.user)
            )
        )