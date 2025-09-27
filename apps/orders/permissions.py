# apps/orders/permissions.py

"""
Order Permissions
"""

from rest_framework import permissions


class IsOrderOwner(permissions.BasePermission):
    """
    Permission to check if user owns the order
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Permission to check if user is admin/staff
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff